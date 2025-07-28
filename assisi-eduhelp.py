import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import groq
import threading
import os

# --- Core Chatbot Class ---
class GroqChatbot:
    """
    A class to interact with the Groq API.
    """
    def __init__(self, api_key):
        """
        Initializes the chatbot with the provided Groq API key.
        
        Args:
            api_key (str): Your Groq API key.
        """
        try:
            self.client = groq.Groq(api_key=api_key)
            # We will maintain a history of the conversation for context.
            self.history = [{"role": "system", "content": "You are a helpful assistant."}]
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize Groq client. Is the API key valid?\nError: {e}")
            self.client = None


    def send_message(self, message):
        """
        Sends a message to the Groq API and returns the response.

        Args:
            message (str): The user's message.

        Returns:
            str: The chatbot's response or an error message.
        """
        if not self.client:
            return "Error: Groq client is not initialized."
            
        # Add user message to history for context
        self.history.append({"role": "user", "content": message})

        try:
            # Make the API request using the chat completions endpoint
            chat_completion = self.client.chat.completions.create(
                messages=self.history,
                model="llama3-8b-8192",  # A fast and capable model available on Groq
            )
            
            # Extract the response text
            bot_response_text = chat_completion.choices[0].message.content
            
            # Add bot response to history for context in future turns
            self.history.append({"role": "assistant", "content": bot_response_text})
            
            return bot_response_text

        except groq.AuthenticationError as e:
            error_message = f"Authentication Error: Invalid API key. Please check your key.\nDetails: {e}"
            print(error_message)
            self.history.pop() # Remove the last user message from history
            return error_message
        except groq.APIConnectionError as e:
            error_message = f"Connection Error: Could not connect to the API. Please check your network.\nDetails: {e.__cause__}"
            print(error_message)
            self.history.pop()
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            print(error_message)
            self.history.pop()
            return error_message

# --- GUI Application Class ---
class ChatbotApp:
    """
    The main GUI application for the chatbot.
    """
    def __init__(self, root):
        """
        Initializes the GUI components.

        Args:
            root (tk.Tk): The main window of the application.
        """
        self.root = root
        self.root.title("Assisi EduHelp")
        self.root.geometry("700x600")
        self.root.configure(bg="#1a1a1a")

        # --- Style Configuration ---
        font_style = ("Helvetica", 12)
        font_style_bold = ("Helvetica", 12, "bold")
        bg_color = "#1a1a1a"
        text_area_bg = "#2a2a2a"
        text_color = "#f0f0f0"
        button_bg = "#f97316" # Groq's orange
        button_fg = "#ffffff"
        button_active_bg = "#ea580c"

        # --- Main Frame ---
        main_frame = tk.Frame(root, bg=bg_color)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Chat Display Area ---
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            bg=text_area_bg,
            fg=text_color,
            font=font_style,
            state='disabled',
            padx=10,
            pady=10,
            bd=0,
            highlightthickness=0
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.tag_config('user', foreground="#a0a0a0", font=font_style_bold)
        self.chat_area.tag_config('bot', foreground="#f97316", font=font_style_bold)
        self.chat_area.tag_config('text', foreground=text_color, font=font_style)

        # --- Input Frame ---
        input_frame = tk.Frame(main_frame, bg=bg_color)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # --- Message Input Box ---
        self.msg_entry = tk.Entry(
            input_frame,
            width=60,
            font=font_style,
            bg=text_area_bg,
            fg=text_color,
            insertbackground=text_color,
            bd=1,
            relief=tk.FLAT
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.msg_entry.bind("<Return>", self.send_message_event)

        # --- Send Button ---
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=font_style_bold,
            bg=button_bg,
            fg=button_fg,
            activebackground=button_active_bg,
            activeforeground=button_fg,
            command=self.send_message_event,
            bd=0,
            padx=20,
            pady=6,
            relief=tk.FLAT
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # --- API Key Configuration & Initialization ---
        # IMPORTANT: Paste your Groq API key between the quotes below
        self.api_key = "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" 

        if not self.api_key or self.api_key == "":
            messagebox.showerror("API Key Missing", "Please enter your Groq API key in the `self.api_key` variable in the code.")
            self.root.destroy()
            return

        self.chatbot = GroqChatbot(api_key=self.api_key)
        if self.chatbot.client:
            self.add_message("System", "Welcome to Assisi EduHelp! You can start chatting now.\n(About: This is made by Ayush Katiyar)")
        else:
            self.root.destroy()
            
    def add_message(self, sender, message):
        """
        Adds a message to the chat display area with appropriate styling.
        
        Args:
            sender (str): 'User', 'Bot', or 'System'.
            message (str): The message content.
        """
        self.chat_area.configure(state='normal')
        
        if sender.lower() in ['user', 'bot']:
            self.chat_area.insert(tk.END, f"{sender}:\n", (sender.lower(),))
            self.chat_area.insert(tk.END, f"{message}\n\n", ('text',))
        else: # System messages
            self.chat_area.insert(tk.END, f"{message}\n\n", ('text',))
            
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message_event(self, event=None):
        """
        Handles the send button click or Enter key press event.
        """
        user_input = self.msg_entry.get()
        if user_input.strip() == "" or self.chatbot is None:
            return

        self.add_message("User", user_input)
        self.msg_entry.delete(0, tk.END)
        
        self.msg_entry.config(state='disabled')
        self.send_button.config(state='disabled')
        self.add_message("Bot", "Thinking...")

        thread = threading.Thread(target=self.get_bot_response, args=(user_input,))
        thread.start()

    def get_bot_response(self, user_input):
        """
        Fetches the bot's response from the API and updates the GUI.
        """
        response = self.chatbot.send_message(user_input)
        self.root.after(0, self.update_chat_with_response, response)

    def update_chat_with_response(self, response):
        """Updates the chat area with the bot's response."""
        self.chat_area.configure(state='normal')
        content = self.chat_area.get("1.0", tk.END)
        last_thinking_pos = content.rfind("Bot:\nThinking...")
        if last_thinking_pos != -1:
            start_index = self.chat_area.index(f"@0,{last_thinking_pos}")
            self.chat_area.delete(start_index, tk.END)
        self.chat_area.configure(state='disabled')

        self.add_message("Bot", response)
        
        self.msg_entry.config(state='normal')
        self.send_button.config(state='normal')
        self.msg_entry.focus_set()


# --- Main Execution ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ChatbotApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred while starting the application: {e}")
