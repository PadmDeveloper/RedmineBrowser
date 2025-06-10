
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
            # Launch browser in headless mode
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            try:
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the issue page
                url = f"https://issue.acmepadm.com:8445/redmine/issues/{issue_id}"
                await page.goto(url)
                
                # Wait for login form and fill credentials
                await page.wait_for_selector('#username')
                await page.fill('#username', self.username)
                await page.fill('#password', self.password)
                
                # Click login button
                await page.click('#login-submit')
                
                # Wait for page to load after login
                await page.wait_for_load_state('networkidle')
                
                # Process notes based on notes_count
                for i in range(notes_count):
                    # Click edit button
                    await page.click('a.icon-edit')
                    
                    # Wait for the notes textarea to be available
                    await page.wait_for_selector('#issue_notes')
                    
                    # Format the note with numbering
                    formatted_note = f"{i + 1}) {note_text}"
                    
                    # Fill the notes textarea
                    await page.fill('#issue_notes', formatted_note)
                    
                    # Check the private notes checkbox
                    await page.check('#issue_private_notes')
                    
                    # Submit the form
                    await page.click('input[type="submit"][value="Submit"]')
                    
                    # Wait for the page to reload
                    await page.wait_for_load_state('networkidle')
                
                return True, f"Successfully added {notes_count} note(s) to issue {issue_id}"
                
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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
