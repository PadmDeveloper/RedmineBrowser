
import os
import asyncio
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class RedmineAutomator:
    def __init__(self):
        self.username = os.environ.get('USERNAME') or os.getenv('USERNAME')
        self.password = os.environ.get('PASSWORD') or os.getenv('PASSWORD')
        
    async def add_note_to_issue(self, issue_id, notes_count, note_text):
        """Automate the process of adding notes to a Redmine issue"""
        async with async_playwright() as p:
            # Launch browser in headless mode using system Chromium
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            
            try:
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the issue page
                url = f"https://issue.acmepadm.com:8445/redmine/issues/{issue_id}"
                await page.goto(url,wait_until='networkidle')
                
                # Wait for login form and fill credentials
                await page.wait_for_selector('input#username')
                await page.fill('input#username', self.username)
                await page.fill('input#password', self.password)
                
                # Click login button
                await page.click('input#login-submit')
                
                # Wait for page to load after login
                await page.wait_for_load_state('networkidle')
                await page.goto(url, wait_until='networkidle')
                
                # Parse notes from the input text (expecting format: 1] note1 \n 2] note2 etc.)
                notes_list = []
                lines = note_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and ']' in line:
                        # Extract text after the bracket
                        parts = line.split(']', 1)
                        if len(parts) == 2 and parts[0].strip().replace('[', '').isdigit():
                            note_content = parts[1].strip()
                            if note_content:
                                notes_list.append(note_content)
                
                # If no properly formatted notes found, use the entire text as one note
                if not notes_list:
                    notes_list = [note_text]
                
                # Process each note separately
                for i, current_note in enumerate(notes_list[:notes_count]):
                    # Click edit button
                    await page.click('a.icon-edit, a[href$="/edit"]')
                    
                    # Wait for the notes textarea to be available
                    await page.wait_for_selector('textarea#issue_notes')
                    
                    # Fill the notes textarea with just the note content
                    await page.fill('textarea#issue_notes', current_note)
                    
                    # Check the private notes checkbox
                    await page.check('input#issue_private_notes')
                    
                    # Submit the form
                    await page.click('input[type=submit][name=commit][value=Submit][data-disable-with=Submit]')
                    
                    # Wait for the page to reload
                    await page.wait_for_load_state('networkidle')
                
                processed_count = min(len(notes_list), notes_count)
                return True, f"Successfully added {processed_count} note(s) to issue {issue_id}"
                
            except Exception as e:
                return False, f"Error: {str(e)}"
            
            finally:
                await browser.close()

# Global automator instance
automator = RedmineAutomator()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "Server is active", "message": "Flask server is running"})

@app.route('/add_note', methods=['POST'])
def add_note():
    """Endpoint to add notes to Redmine issue"""
    try:
        data = request.json
        issue_id = data.get('issue_id')
        notes_count = data.get('notes_count')
        note_text = data.get('note_text')
        
        if not all([issue_id, notes_count, note_text]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(
            automator.add_note_to_issue(issue_id, int(notes_count), note_text)
        )
        loop.close()
        
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 500
            
    except Exception as e:
        # Log the exception or print it for debugging
        print(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

