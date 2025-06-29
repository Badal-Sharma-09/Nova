import os
import re
from google.generativeai import GenerativeModel, configure, list_models
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from tkinter import font as tkfont
import html
from tkinter.font import Font
import webbrowser
from io import StringIO
from utils.gemini_bot import get_gemini_model, get_gemini_response

# Configure the Gemini API
def setup_gemini():
    """Configure and set up the Gemini AI client."""
    try:
        # Get API key from environment variable or set it directly
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
            api_key = input("Please enter your Gemini API key: ")
        
        # Configure the Gemini API
        configure(api_key=api_key)
        print("Gemini API configured successfully.")
        
        return True
    except Exception as e:
        print(f"Error setting up Gemini API: {e}")
        return False

# List available models to debug
def check_available_models():
    """List all available models to help identify the correct model name."""
    try:
        models = list_models()
        print("Available models:")
        for model in models:
            print(f"- {model.name}")
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

# Enhanced Rich Text Widget
class RichText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Create text tags for formatting
        self.tag_configure("bold", font=Font(family="", size=0, weight="bold"))
        self.tag_configure("italic", font=Font(family="", size=0, slant="italic"))
        self.tag_configure("code", background="#f0f0f0", font=Font(family="Courier", size=10))
        self.tag_configure("code_block", background="#f5f5f5", font=Font(family="Courier", size=10))
        self.tag_configure("heading1", font=Font(family="", size=14, weight="bold"))
        self.tag_configure("heading2", font=Font(family="", size=12, weight="bold"))
        self.tag_configure("heading3", font=Font(family="", size=11, weight="bold"))
        self.tag_configure("bullet", lmargin1=20, lmargin2=40)
        self.tag_configure("user", foreground="#007bff")
        self.tag_configure("assistant", foreground="#28a745")
        self.tag_configure("link", foreground="blue", underline=1)
        
        # Make text widget read-only by default
        self.config(state=tk.DISABLED)
        
        # Add binding for clickable links
        self.tag_bind("link", "<Button-1>", self._follow_link)
        
    def _follow_link(self, event):
        """Open links when clicked"""
        tag_indices = self.tag_prevrange("link", f"@{event.x},{event.y}")
        if tag_indices:
            url = self.get(*tag_indices)
            webbrowser.open(url)
    
    def clear(self):
        """Clear all content from the text widget"""
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)
    
    def append_user_message(self, text):
        """Add user message with appropriate styling"""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, "You: ", "user")
        self.insert(tk.END, text + "\n\n")
        self.see(tk.END)
        self.config(state=tk.DISABLED)
    
    def append_ai_message(self, text):
        """Add AI message with proper formatting of markdown elements"""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, "Gemini: ", "assistant")
        
        # Process and render the text with proper formatting
        self._render_formatted_text(text)
        
        self.insert(tk.END, "\n\n")
        self.see(tk.END)
        self.config(state=tk.DISABLED)
    
    def _render_formatted_text(self, text):
        """Render text with markdown formatting"""
        # Process the text line by line for block elements
        lines = text.splitlines()
        i = 0
        
        in_code_block = False
        code_block_content = []
        code_language = ""
        
        while i < len(lines):
            line = lines[i]
            
            # Check for code blocks
            if line.startswith("```"):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    # Extract language if specified
                    if len(line) > 3:
                        code_language = line[3:].strip()
                    code_block_content = []
                else:
                    # End of code block - render it
                    in_code_block = False
                    lang_text = f" [{code_language}]" if code_language else ""
                    self.insert(tk.END, f"Code Block{lang_text}:\n", "heading3")
                    code_text = "\n".join(code_block_content)
                    self.insert(tk.END, code_text + "\n", "code_block")
                    code_language = ""
                i += 1
                continue
            elif in_code_block:
                # Inside code block - collect content
                code_block_content.append(line)
                i += 1
                continue
            
            # Check for headings
            if line.startswith("# "):
                self.insert(tk.END, line[2:] + "\n", "heading1")
                i += 1
                continue
            elif line.startswith("## "):
                self.insert(tk.END, line[3:] + "\n", "heading2")
                i += 1
                continue
            elif line.startswith("### "):
                self.insert(tk.END, line[4:] + "\n", "heading3")
                i += 1
                continue
            
            # Check for bullet points
            elif line.strip().startswith("- ") or line.strip().startswith("* "):
                marker = line.strip()[0]
                indent = len(line) - len(line.lstrip())
                bullet_text = line.strip()[2:]
                
                # Process inline formatting in bullet points
                self.insert(tk.END, "  • ", "bullet")
                self._process_inline_formatting(bullet_text)
                self.insert(tk.END, "\n")
                i += 1
                continue
            
            # Regular paragraph with inline formatting
            else:
                # Process inline formatting
                if line.strip():  # Only process non-empty lines
                    self._process_inline_formatting(line)
                    self.insert(tk.END, "\n")
                else:
                    self.insert(tk.END, "\n")  # Empty line
                i += 1
    
    def _process_inline_formatting(self, text):
        """Process inline markdown formatting like bold, italic, code"""
        # First, break the text into segments based on formatting characters
        segments = []
        current_text = ""
        i = 0
        
        while i < len(text):
            # Bold with double asterisks or underscores
            if i + 1 < len(text) and (text[i:i+2] == "**" or text[i:i+2] == "__"):
                if current_text:
                    segments.append(("regular", current_text))
                    current_text = ""
                
                marker = text[i:i+2]
                i += 2
                bold_text = ""
                
                while i < len(text):
                    if i + 1 < len(text) and text[i:i+2] == marker:
                        i += 2
                        break
                    bold_text += text[i]
                    i += 1
                
                segments.append(("bold", bold_text))
                continue
                
            # Italic with single asterisks or underscores
            elif text[i] == "*" or text[i] == "_":
                if text[i-1:i] != "\\" and i-1 >= 0:  # Not escaped
                    if current_text:
                        segments.append(("regular", current_text))
                        current_text = ""
                    
                    marker = text[i]
                    i += 1
                    italic_text = ""
                    
                    while i < len(text):
                        if text[i] == marker and text[i-1:i] != "\\":
                            i += 1
                            break
                        italic_text += text[i]
                        i += 1
                    
                    segments.append(("italic", italic_text))
                    continue
            
            # Inline code with backticks
            elif text[i] == "`":
                if current_text:
                    segments.append(("regular", current_text))
                    current_text = ""
                
                i += 1
                code_text = ""
                
                while i < len(text):
                    if text[i] == "`":
                        i += 1
                        break
                    code_text += text[i]
                    i += 1
                
                segments.append(("code", code_text))
                continue
            
            current_text += text[i]
            i += 1
        
        if current_text:
            segments.append(("regular", current_text))
        
        # Now insert segments with appropriate tags
        for segment_type, segment_text in segments:
            if segment_type == "bold":
                self.insert(tk.END, segment_text, "bold")
            elif segment_type == "italic":
                self.insert(tk.END, segment_text, "italic")
            elif segment_type == "code":
                self.insert(tk.END, segment_text, "code")
            else:
                self.insert(tk.END, segment_text)

# Main application class
class GeminiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini AI Interface")
        self.root.geometry("900x700")
        
        # Set up the Gemini API
        setup_gemini()
        
        # Variables for toggles
        self.render_markdown_var = tk.BooleanVar(value=True)
        self.highlight_code_var = tk.BooleanVar(value=True)
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create toggle frame
        toggle_frame = ttk.Frame(main_frame)
        toggle_frame.pack(fill=tk.X, pady=5)
        
        # Create toggles
        ttk.Checkbutton(toggle_frame, text="Render Markdown", variable=self.render_markdown_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(toggle_frame, text="Highlight Code", variable=self.highlight_code_var).pack(side=tk.LEFT, padx=5)
        
        # Create clear button
        ttk.Button(toggle_frame, text="Clear Chat", command=self.clear_chat).pack(side=tk.RIGHT, padx=5)
        
        # Chat history display (using custom formatter)
        ttk.Label(main_frame, text="Chat History:").pack(anchor=tk.W)
        
        # Create chat frame with scrollbars
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create vertical scrollbar
        y_scrollbar = ttk.Scrollbar(chat_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create rich text display for chat
        self.chat_display = RichText(
            chat_frame, 
            wrap=tk.WORD, 
            font=("Segoe UI", 10),
            padx=5, 
            pady=5,
            xscrollcommand=x_scrollbar.set,
            yscrollcommand=y_scrollbar.set
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.chat_display.yview)
        x_scrollbar.config(command=self.chat_display.xview)
        
        # User input section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Your Message:").pack(anchor=tk.W)
        
        # Create text input frame with scrollbar
        text_input_frame = ttk.Frame(input_frame)
        text_input_frame.pack(fill=tk.X, pady=5)
        
        # Create scrollbar for user input
        input_scrollbar = ttk.Scrollbar(text_input_frame)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create input text widget
        self.user_input = tk.Text(text_input_frame, height=5, wrap=tk.WORD, font=("Segoe UI", 10))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Connect scrollbar to input text
        self.user_input.config(yscrollcommand=input_scrollbar.set)
        input_scrollbar.config(command=self.user_input.yview)
        
        # Bottom frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Send button
        send_button = ttk.Button(button_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(button_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to send message
        self.user_input.bind("<Control-Return>", lambda event: self.send_message())
        
        # Store conversation history
        self.chat_history = []
        
        # Welcome message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Gemini: ", "assistant")
        self.chat_display.insert(tk.END, "Hello! I'm ready to help. Type a message and press Send or Ctrl+Enter.\n\n")
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear the chat display and history"""
        self.chat_display.clear()
        self.chat_history = []
        
        # Add welcome message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Gemini: ", "assistant")
        self.chat_display.insert(tk.END, "Chat cleared. How can I help you?\n\n")
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send user message and get response from Gemini"""
        msg = self.user_input.get("1.0", tk.END).strip()
        if not msg:
            return
        
        # Display user message
        self.chat_display.append_user_message(msg)
        
        # Add to history
        self.chat_history.append({"role": "user", "parts": [msg]})
        
        # Clear input
        self.user_input.delete("1.0", tk.END)
        
        # Update status
        self.status_var.set("Thinking...")
        
        # Create a loading indicator
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Gemini: ", "assistant")
        loading_mark = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, "Thinking...\n")
        self.chat_display.config(state=tk.DISABLED)
        
        # Get response in a background thread
        def get_response_thread():
            try:
                # Get raw response from Gemini
                response = get_gemini_response(msg, history=self.chat_history[:-1])  # Exclude last message
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_with_response(response, loading_mark))
            except Exception as e:
                self.root.after(0, lambda: self.handle_error(str(e), loading_mark))
        
        # Start background thread
        threading.Thread(target=get_response_thread).start()
    
    def update_with_response(self, response, loading_mark):
        """Update the UI with the model's response"""
        # Remove loading indicator
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(loading_mark, f"{loading_mark} lineend+1c")
        self.chat_display.config(state=tk.DISABLED)
        
        # Display formatted response
        if self.render_markdown_var.get():
            self.chat_display.append_ai_message(response)
        else:
            # Plain text mode
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, response + "\n\n")
            self.chat_display.config(state=tk.DISABLED)
        
        # Add to history
        self.chat_history.append({"role": "model", "parts": [response]})
        
        # Update status
        self.status_var.set("Ready")
    
    def handle_error(self, error_msg, loading_mark):
        """Handle errors in the API call"""
        # Remove loading indicator
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(loading_mark, f"{loading_mark} lineend+1c")
        
        # Display error message
        self.chat_display.insert(tk.END, f"Error: {error_msg}\n\n", "assistant")
        self.chat_display.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set("Error occurred")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gemini AI Chat")
    app = GeminiApp(root)
    root.mainloop()