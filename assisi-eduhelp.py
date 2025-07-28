# --- IMPORT LIBRARIES ---

# 'tkinter' is Python's standard library for creating graphical user interfaces (GUIs).
# We give it a shorter name 'tk' to make it easier to type.
import tkinter as tk

# We also import specific parts of tkinter:
# 'scrolledtext' for a text box with a scrollbar.
# 'messagebox' for showing pop-up alerts and error messages.
from tkinter import scrolledtext, messagebox

# 'groq' is the library that lets us connect to the Groq AI service and use LLM model through API
import groq

# 'threading' allows us to run tasks in the background. This is crucial
# so our application doesn't freeze while waiting for the AI's response.
import threading


# --- THE CHATBOT'S BRAIN ---
# This class handles all the logic for talking to the Groq AI.
class GroqChatbot:
    
    # This is the "constructor" method. It runs automatically when we create a new GroqChatbot object.
    def __init__(self, api_key):
        # 'self' refers to the specific object being created.
        # We use a 'try...except' block to gracefully handle potential errors.
        try:
            # We initialize the connection to Groq using the provided API key.
            # self.client will hold our connection object.
            self.client = groq.Groq(api_key=api_key)
            
            # self.history is a list that will store the entire conversation.
            # It's a list of dictionaries, which is the format Groq requires.
            # We start it with a "system" message to tell the AI its personality.
            self.history = [{"role": "system", "content": "You are a helpful assistant."}]

        # If any error ('Exception') happens in the 'try' block...
        except Exception as e:
            # ...we show a pop-up error message to the user.
            messagebox.showerror("Initialization Error", f"Failed to initialize Groq client. Is the API key valid?\nError: {e}")
            # And we set the client to None to show that the connection failed.
            self.client = None

    # This method sends a user's message to the Groq API and gets a response.
    def send_message(self, message):
        # First, check if the connection to Groq was successful.
        if not self.client:
            return "Error: Groq client is not initialized."
            
        # We add the user's new message to our conversation history.
        # This gives the AI context about what has been said before.
        self.history.append({"role": "user", "content": message})

        # We put the API call in a 'try...except' block because it involves
        # the internet and could fail for many reasons.
        try:
            # This is the actual API call. We send our entire message history.
            # We also specify which AI model we want to use.
            chat_completion = self.client.chat.completions.create(
                messages=self.history,
                model="llama3-8b-8192", 
            )
            
            # The AI's response is nested inside the object it sends back.
            # This line extracts the actual text of the message.
            bot_response_text = chat_completion.choices[0].message.content
            
            # We add the AI's response to our history as well, so it remembers its own replies.
            self.history.append({"role": "assistant", "content": bot_response_text})
            
            # Finally, we return the AI's response text to be displayed in the app.
            return bot_response_text

        # The following 'except' blocks catch specific types of errors.
        except groq.AuthenticationError as e:
            error_message = f"Authentication Error: Invalid API key. Please check your key.\nDetails: {e}"
            print(error_message) # Print the error for debugging.
            self.history.pop() # If it fails, remove the user's last message from history.
            return error_message # Return the error message to be displayed.

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


# --- THE APPLICATION'S VISUALS AND LAYOUT ---
# This class builds the GUI (Graphical User Interface) that the user sees and interacts with.
class ChatbotApp:

    # The constructor method, which sets up the entire window when a ChatbotApp object is created.
    # 'root' is the main window of our application.
    def __init__(self, root):
        # --- Basic Window Setup ---
        self.root = root
        self.root.title("Assisi EduHelp") # Set the text in the title bar.
        self.root.geometry("700x600")     # Set the initial size of the window (width x height).
        self.root.configure(bg="#1a1a1a") # Set the background color of the window.

        # --- Style Variables ---
        # Storing styles in variables makes it easy to change the app's look later.
        font_style = ("Helvetica", 12)
        font_style_bold = ("Helvetica", 12, "bold")
        bg_color = "#1a1a1a"
        text_area_bg = "#2a2a2a"
        text_color = "#f0f0f0"
        button_bg = "#f97316" # A nice orange color.
        button_fg = "#ffffff"
        button_active_bg = "#ea580c"

        # --- Create the Main Container ---
        # A 'Frame' is an invisible container used to organize other widgets.
        main_frame = tk.Frame(root, bg=bg_color)
        # '.pack()' is a method to place the widget in the window.
        # 'padx' and 'pady' add some padding (space) around the frame.
        # 'fill=tk.BOTH' makes the frame fill the window in both directions.
        # 'expand=True' allows the frame to grow if the window is resized.
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Create the Chat Display Area ---
        # This is the main text box where the conversation will be shown.
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,            # Wraps long lines of text by word.
            bg=text_area_bg,         # Background color.
            fg=text_color,           # Text color.
            font=font_style,         # The font to use.
            state='disabled',        # IMPORTANT: Makes the text area read-only.
            padx=10, pady=10,        # Padding inside the text area.
            bd=0, highlightthickness=0 # Removes the border.
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # --- Configure Text Colors (Tags) ---
        # Tags let us apply different styles to different parts of the text.
        self.chat_area.tag_config('user', foreground="#a0a0a0", font=font_style_bold)
        self.chat_area.tag_config('bot', foreground="#f97316", font=font_style_bold)
        self.chat_area.tag_config('text', foreground=text_color, font=font_style)

        # --- Create the Bottom Frame for Input and Button ---
        input_frame = tk.Frame(main_frame, bg=bg_color)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # --- Create the User Message Input Box ---
        # An 'Entry' widget is a single-line text box.
        self.msg_entry = tk.Entry(input_frame, font=font_style, bg=text_area_bg, fg=text_color)
        self.msg_entry.config(insertbackground=text_color, bd=1, relief=tk.FLAT) # Style the cursor and border.
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8) # 'ipady' makes the box taller.
        
        # This line makes the "Enter" key trigger the 'send_message_event' function.
        self.msg_entry.bind("<Return>", self.send_message_event)

        # --- Create the Send Button ---
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=font_style_bold,
            bg=button_bg, fg=button_fg,
            activebackground=button_active_bg, # Color when the button is clicked.
            activeforeground=button_fg,
            command=self.send_message_event, # Function to call when clicked.
            bd=0, padx=20, pady=6, relief=tk.FLAT # Style the button.
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # --- API Key Setup and Chatbot Initialization ---
        # ⚠️ SECURITY WARNING: Never leave API keys directly in your code like this.
        # This is okay for a simple personal project, but for anything else, you should
        # load keys from a secure file or an environment variable.
        self.api_key = "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" 

        # Check if the API key is missing.
        if not self.api_key or self.api_key == "":
            messagebox.showerror("API Key Missing", "Please enter your Groq API key in the `self.api_key` variable in the code.")
            self.root.destroy() # Close the application if the key is missing.
            return

        # Create an instance of our chatbot 'brain'.
        self.chatbot = GroqChatbot(api_key=self.api_key)
        
        # If the chatbot connection was successful, display a welcome message.
        if self.chatbot.client:
            self.add_message("System", "Welcome to Assisi EduHelp! You can start chatting now.")
        # Otherwise, the constructor already showed an error, so just close the app.
        else:
            self.root.destroy()
            
    # This method adds a new message to the chat display area.
    def add_message(self, sender, message):
        # We must temporarily enable the text area to add new text.
        self.chat_area.configure(state='normal')
        
        # We check the sender to apply the correct color tag.
        if sender.lower() in ['user', 'bot']:
            self.chat_area.insert(tk.END, f"{sender}:\n", (sender.lower(),)) # Insert the "User:" or "Bot:" label with its color.
            self.chat_area.insert(tk.END, f"{message}\n\n", ('text',))       # Insert the message text with the default color.
        else: # For 'System' messages.
            self.chat_area.insert(tk.END, f"{message}\n\n", ('text',))
            
        # We disable the text area again to make it read-only for the user.
        self.chat_area.configure(state='disabled')
        # This automatically scrolls the chat to the very bottom to show the latest message.
        self.chat_area.yview(tk.END)

    # This function is triggered when the user clicks 'Send' or presses Enter.
    def send_message_event(self, event=None):
        # Get the text currently in the input box.
        user_input = self.msg_entry.get()
        # If the input is just empty spaces or the chatbot isn't working, do nothing.
        if user_input.strip() == "" or self.chatbot is None:
            return

        # Add the user's message to the chat window.
        self.add_message("User", user_input)
        # Clear the input box for the next message.
        self.msg_entry.delete(0, tk.END)
        
        # --- PREPARE FOR AI RESPONSE ---
        # Disable the input box and send button so the user can't send another message while waiting.
        self.msg_entry.config(state='disabled')
        self.send_button.config(state='disabled')
        # Show a "Thinking..." message so the user knows the app is working.
        self.add_message("Bot", "Thinking...")

        # --- USE THREADING FOR RESPONSIVENESS ---
        # We create a new thread to run the 'get_bot_response' function.
        # This lets the API call happen in the background without freezing the GUI.
        thread = threading.Thread(target=self.get_bot_response, args=(user_input,))
        thread.start() # Start the background task.

    # This method runs IN THE BACKGROUND THREAD.
    def get_bot_response(self, user_input):
        # This is the slow part: it calls the chatbot brain to get a response from the internet.
        response = self.chatbot.send_message(user_input)
        # IMPORTANT: You cannot directly update the GUI from a background thread.
        # So, we use 'root.after(0, ...)' to schedule the 'update_chat_with_response'
        # function to be run safely on the main GUI thread.
        self.root.after(0, self.update_chat_with_response, response)

    # This method runs back ON THE MAIN GUI THREAD to safely update the window.
    def update_chat_with_response(self, response):
        # To delete the "Thinking..." text, we must enable the chat area.
        self.chat_area.configure(state='normal')
        
        # Get all the text content from the chat area.
        content = self.chat_area.get("1.0", tk.END)
        # Find the position of the last "Thinking..." message.
        last_thinking_pos = content.rfind("Bot:\nThinking...")
        
        # If we found it...
        if last_thinking_pos != -1:
            # ...calculate the starting index and delete it.
            start_index = self.chat_area.index(f"@0,{last_thinking_pos}")
            self.chat_area.delete(start_index, tk.END)

        # Disable the chat area again.
        self.chat_area.configure(state='disabled')

        # Now, add the actual response from the bot.
        self.add_message("Bot", response)
        
        # Re-enable the input box and send button for the user's next message.
        self.msg_entry.config(state='normal')
        self.send_button.config(state='normal')
        
        # Automatically place the cursor back in the input box.
        self.msg_entry.focus_set()


# --- START THE APPLICATION ---
# The 'if __name__ == "__main__":' block is standard Python practice.
# The code inside it only runs when the script is executed directly.
if __name__ == "__main__":
    try:
        # Create the main application window.
        root = tk.Tk()
        # Create an instance of our ChatbotApp class, passing the main window to it.
        app = ChatbotApp(root)
        # 'root.mainloop()' starts the tkinter event loop. This line makes the window
        # appear, listen for events (like clicks and key presses), and keeps it running.
        root.mainloop()
    except Exception as e:
        # Catch any other unexpected errors during startup.
        print(f"An error occurred while starting the application: {e}")
