# ucp_llm_profile_manager.py
# Copyright (c) 2024 Sameh Yassin
# All rights reserved.
#
# This project, "UCP-LLM (User Context Protocol for Large Language Models)",
# including its conceptual framework, HTML generator, Python library,
# and GUI manager, is the intellectual property of Sameh Yassin.
#
# Version: 1.0.0

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
import json
from typing import Optional, Dict, Any, List

# Attempt to import the UCPProfile library
try:
    from ucp_llm import UCPProfile # Assuming ucp_llm.py is in the same directory
except ImportError:
    messagebox.showerror("Import Error", "Could not find the 'ucp_llm.py' library file.\nPlease ensure it is in the same directory as this program.")
    exit()

class UCPManagerApp:
    def __init__(self, master_root):
        self.master = master_root
        master_root.title("UCP-LLM Profile Manager - v1.0.0")
        master_root.geometry("1000x800") # Slightly wider for English labels
        master_root.configure(bg="#eaf0f8") # Light blue-grey background

        self.ucp_profile_loader: Optional[UCPProfile] = None
        self.current_file_path: Optional[str] = None
        self.loaded_ucp_data: Optional[Dict[str, Any]] = None # This will hold the mutable data for editing

        # --- Styling ---
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("TButton", padding=7, relief="flat", font=('Arial', 10), borderwidth=1)
        style.configure("TButton", background="#d1d8e0", foreground="#2f3542") # Softer button colors
        style.map("TButton", background=[('active', '#b2bec3'), ('disabled', '#dfe4ea')])
        
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground="#192a56", padding=(0,10,0,5), background="#eaf0f8")
        style.configure("SectionTitle.TLabel", font=("Arial", 12, "bold"), foreground="#273c75", padding=(0,5,0,3), background="#eaf0f8")
        # FieldKey.TLabel needs careful width adjustment for English labels
        style.configure("FieldKey.TLabel", font=("Arial", 10, "bold"), foreground="#40407a", background="#ffffff", width=35, anchor="w", justify=tk.LEFT, padding=(5,0,0,0)) 
        style.configure("FieldValue.TLabel", font=("Arial", 10), wraplength=500, background="#ffffff", foreground="#2c2c54", anchor="w", justify=tk.LEFT)
        
        style.configure("Main.TFrame", background="#eaf0f8")
        style.configure("SectionDisplay.TFrame", background="#ffffff", relief="groove", borderwidth=1, padding=10) # Groove for section
        style.configure("ItemCard.TFrame", background="#f5f6fa", relief="solid", borderwidth=1, padding=7, bordercolor="#ced6e0") # Lighter item card
        style.configure("FieldRow.TFrame", background="#ffffff")

        # --- Top Frame for File Operations ---
        top_frame = ttk.Frame(master_root, style="Main.TFrame", padding=(10,10,10,0))
        top_frame.pack(fill=tk.X)

        self.load_button = ttk.Button(top_frame, text="Load UCP-LLM File (JSON)", command=self.load_ucp_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(top_frame, text="Save Changes (JSON)", command=self.save_ucp_file_as_json, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.export_text_button = ttk.Button(top_frame, text="Export as Formatted Text", command=self.export_as_formatted_text, state=tk.DISABLED)
        self.export_text_button.pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(top_frame, text="No file loaded.", anchor="w", background="#eaf0f8", foreground="#333a45")
        self.file_label.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)


        # --- Main Display Area (Canvas + Scrollbar) ---
        main_canvas_frame = ttk.Frame(master_root, style="Main.TFrame", padding=(10,0,10,10))
        main_canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(main_canvas_frame, bg="#eaf0f8", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(main_canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.display_frame = ttk.Frame(self.canvas, style="Main.TFrame", padding=10) 
        self.canvas_window = self.canvas.create_window((0, 0), window=self.display_frame, anchor="nw")
        
        # Event bindings for scrolling
        self.display_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        master_root.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")) # For Windows
        master_root.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units")) # For Linux
        master_root.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # For Linux
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(master_root, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=5, background="#cad3c8", foreground="#1e272e")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status("Welcome! Please load a UCP-LLM JSON file (generated by UCP-LLM Generator v1.0.0).")

    def _update_status(self, message: str):
        self.status_bar.config(text=message)

    def _clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def _add_header(self, text: str, level: int = 1, parent_widget: Optional[tk.Widget] = None):
        parent = parent_widget if parent_widget else self.display_frame
        style = "Header.TLabel" if level == 1 else "SectionTitle.TLabel"
        anchor_pos = "center" if level == 1 else "w" # English is LTR, so "w" for section titles
        ttk.Label(parent, text=text, style=style, anchor=anchor_pos).pack(fill=tk.X, pady=(10 if level==1 else 7, 3))

    def _add_display_field(self, parent_frame: tk.Widget, 
                           english_label: str, # This is the display label
                           value: Any, 
                           section_id_for_edit: Optional[str] = None, 
                           item_index_for_edit: Optional[int] = None, 
                           json_key_for_edit: Optional[str] = None, # This is the English JSON key
                           is_multiline: bool = False):
        field_container = ttk.Frame(parent_frame, style="FieldRow.TFrame") 
        field_container.pack(fill=tk.X, pady=1, padx=0)

        key_text_for_label = f"{english_label}:"
        key_label_widget = ttk.Label(field_container, text=key_text_for_label, style="FieldKey.TLabel") 
        key_label_widget.pack(side=tk.LEFT, padx=(0,5)) # Label on the left for LTR

        val_str = str(value) if value is not None and str(value).strip() != "" else "(Not specified)"
        
        value_widget_frame = ttk.Frame(field_container, style="FieldRow.TFrame")
        value_widget_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

        if is_multiline:
            # Using a Text widget for multiline display, disabled for read-only
            value_display_widget = tk.Text(value_widget_frame, wrap=tk.WORD, height=3, width=50,
                                           font=('Arial', 10), relief=tk.FLAT, borderwidth=0, 
                                           bg="#ffffff", fg="#102a43", padx=3, pady=3,
                                           spacing1=2, spacing3=2) # Added spacing for readability
            value_display_widget.insert(tk.END, val_str)
            value_display_widget.config(state=tk.DISABLED)
            value_display_widget.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        else:
            value_display_widget = ttk.Label(value_widget_frame, text=val_str, style="FieldValue.TLabel")
            value_display_widget.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        
        if section_id_for_edit and json_key_for_edit:
            edit_button = ttk.Button(value_widget_frame, text="✏️", width=3,
                                     command=lambda s_id=section_id_for_edit, 
                                                    idx=item_index_for_edit, 
                                                    k_edit=json_key_for_edit, # Pass the English JSON key
                                                    lbl=english_label, 
                                                    current_val=value: 
                                     self.edit_field_value(s_id, idx, k_edit, lbl, current_val))
            edit_button.pack(side=tk.LEFT, padx=(5,0)) 

    def edit_field_value(self, section_id: str, item_index: Optional[int], 
                         json_key_to_edit: str, # Now using English JSON key
                         english_label_for_prompt: str, current_value: Any):
        if not self.loaded_ucp_data: return
        
        prompt_message = f"Current value for '{english_label_for_prompt}':\n{current_value}\n\nEnter new value:"
        # For multiline, a Toplevel with Text widget would be better. For now, simpledialog.
        new_value_str = simpledialog.askstring(f"Edit: {english_label_for_prompt}", prompt_message, parent=self.master)

        if new_value_str is not None: # User entered something or cleared it (empty string)
            data_changed = False
            # Locate the section and item in the self.loaded_ucp_data (which is a mutable dict)
            for section_data_dict in self.loaded_ucp_data.get("sections", []):
                if section_data_dict.get("id") == section_id:
                    items_list = section_data_dict.get("items", [])
                    if item_index is not None: # Editing a field within a specific item of a list
                        if 0 <= item_index < len(items_list):
                            if isinstance(items_list[item_index], dict):
                                items_list[item_index][json_key_to_edit] = new_value_str # Update using English JSON key
                                data_changed = True
                            else: # Should not happen if JSON is well-formed by generator
                                messagebox.showerror("Internal Error", f"Item at index {item_index} in section '{section_id}' is not a dictionary.", parent=self.master)
                                return
                        else: # Invalid item_index
                            messagebox.showerror("Error", f"Item index ({item_index}) is out of bounds for section '{section_id}'.", parent=self.master)
                            return
                    # else: This branch would be for sections that are single-item but not structured as a list (not our case)
                    break # Found the section
            
            if data_changed:
                self.display_protocol_content_structured() # Re-render the display with new data
                self._update_status(f"'{english_label_for_prompt}' updated. Click 'Save Changes' to persist.")
                self.save_button.config(state=tk.NORMAL)
                self.export_text_button.config(state=tk.NORMAL) # Re-enable export as content changed
            # No "else" needed here, as simpledialog returns None if cancelled, empty string if cleared.
            # An empty string is a valid new value.

    def load_ucp_file(self):
        try:
            filepath = filedialog.askopenfilename(
                title="Select UCP-LLM JSON File (English Keys)", filetypes=(("JSON files", "*.json"),("All files", "*.*")))
            if not filepath: self._update_status("File load cancelled."); return
            
            self.ucp_profile_loader = UCPProfile(filepath) 
            
            if self.ucp_profile_loader.get_error():
                messagebox.showerror("File Load Error", f"Failed to load or parse file:\n{self.ucp_profile_loader.get_error()}")
                self._reset_app_state(); return
            
            self.loaded_ucp_data = self.ucp_profile_loader.get_raw_data() # Get mutable dict for editing
            if not self.loaded_ucp_data or not self.ucp_profile_loader.is_valid(): # Double check
                messagebox.showerror("File Content Error", "File is empty or does not follow the expected UCP-LLM structure.")
                self._reset_app_state(); return

            self.current_file_path = filepath
            tool_version = self.ucp_profile_loader.get_generator_tool_version() or 'Unknown Version'
            
            # Attempt to get a user identifier (e.g., preferredName from 'personal' section)
            user_identifier = self.ucp_profile_loader.get_personal_preferred_name() or "(Not Specified)"

            self.file_label.config(text=f"File: ...{self.current_file_path[-45:]} (Tool: {tool_version})")
            self.display_protocol_content_structured() 
            self.save_button.config(state=tk.NORMAL) 
            self.export_text_button.config(state=tk.NORMAL)
            self._update_status(f"Protocol loaded successfully for user: {user_identifier}")

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
            self._reset_app_state()

    def _reset_app_state(self):
        """Resets application state when a file load fails or is invalid."""
        self.ucp_profile_loader = None
        self.current_file_path = None
        self.loaded_ucp_data = None
        self.file_label.config(text="No file loaded.")
        self._clear_display_frame()
        self.save_button.config(state=tk.DISABLED)
        self.export_text_button.config(state=tk.DISABLED)
        self._update_status("File operation failed or file invalid. Please try again.")

    def save_ucp_file_as_json(self):
        if not self.loaded_ucp_data or not self.current_file_path:
            messagebox.showwarning("No Data", "Please load and modify a protocol first.", parent=self.master)
            return
        try:
            # Suggest the current filename by default for saving
            initial_filename = self.current_file_path.split('/')[-1]
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON files", "*.json")],
                title="Save Modified Protocol as JSON", initialfile=initial_filename )
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(self.loaded_ucp_data, f, ensure_ascii=False, indent=2) # Save the edited data
                messagebox.showinfo("Success", f"Modified protocol saved successfully to:\n{save_path}", parent=self.master)
                self._update_status(f"Protocol saved to {save_path.split('/')[-1]}")
                self.current_file_path = save_path # Update current file path if saved to a new location
                self.file_label.config(text=f"File: ...{self.current_file_path[-45:]}")
            else: self._update_status("Save operation cancelled.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the file: {str(e)}", parent=self.master)
            self._update_status("Failed to save file.")

    def display_protocol_content_structured(self):
        """Displays all content from the loaded UCP-LLM JSON using English labels."""
        self._clear_display_frame()
        if not self.ucp_profile_loader or not self.loaded_ucp_data:
            ttk.Label(self.display_frame, text="No data to display.", style="Header.TLabel").pack(pady=20)
            return

        # Use self.ucp_profile_loader for READ-ONLY access to display structure from library
        # But use self.loaded_ucp_data (the mutable dict) to pass current_value to edit_field_value

        tool_version = self.ucp_profile_loader.get_generator_tool_version() or 'N/A'
        gen_date = self.ucp_profile_loader.get_generation_date() or 'N/A'

        self._add_header(f"User Context Protocol (Tool v: {tool_version})")
        self._add_display_field(self.display_frame, "File Generation Date", gen_date)
        ttk.Separator(self.display_frame, orient='horizontal').pack(fill='x', pady=10, padx=5)

        # --- Mapping of section_id to English Display Title for sections ---
        # This should align with the 'title' field your HTML generator puts in the JSON for each section.
        # It assumes the library's get_section_title(section_id) returns this English title.
        
        for section_data_from_json in self.ucp_profile_loader.get_sections(): # Iterate over sections from raw JSON
            section_id = section_data_from_json.get("id")
            # Use the 'title' field directly from the JSON section data for display
            section_display_title = section_data_from_json.get("title", f"Section: {section_id}") 
            if not section_id: continue

            self._add_header(section_display_title, level=2)
            
            section_display_container = ttk.Frame(self.display_frame, style="SectionDisplay.TFrame")
            section_display_container.pack(fill=tk.X, expand=True, pady=5)

            # Get items for this section from the mutable self.loaded_ucp_data
            current_section_in_editable_data = next((s for s in self.loaded_ucp_data.get("sections",[]) if s.get("id") == section_id), None)
            items_to_display = current_section_in_editable_data.get("items", []) if current_section_in_editable_data else []


            if not items_to_display:
                self._add_display_field(section_display_container, "(This section is empty)", "")
            
            for item_index, item_data_dict_editable in enumerate(items_to_display):
                parent_for_fields = section_display_container
                if len(items_to_display) > 1 : 
                     item_card = ttk.Frame(section_display_container, style="ItemCard.TFrame")
                     item_card.pack(fill=tk.X, pady=(5,10), padx=5) 
                     # Display item number if multiple items
                     ttk.Label(item_card, text=f"Item ({item_index + 1})", font=('Arial', 10, 'italic'), anchor="w", style="FieldValue.TLabel").pack(fill=tk.X, pady=(0,5))
                     parent_for_fields = item_card

                # To get the English labels for display, we refer to the HTML sectionTypeData structure
                # This requires that the Tkinter app has access to a similar structure or a mapping.
                # For simplicity, we'll use the JSON key as the display label if no other mapping is present.
                # A more robust solution would involve a shared definition or passing labels.
                
                html_section_def = self.get_html_section_definition(section_id) # You'll need to implement this helper

                for json_key_from_item, value_from_item in item_data_dict_editable.items():
                    display_label_for_field = json_key_from_item # Default to jsonKey
                    if html_section_def:
                        field_def_from_html = next((f for f in html_section_def.get("fields", []) if f.get("jsonKey") == json_key_from_item), None)
                        if field_def_from_html:
                            display_label_for_field = field_def_from_html.get("label", json_key_from_item) # Use HTML label

                    is_multiline_display = isinstance(value_from_item, str) and ("\n" in value_from_item or len(value_from_item) > 70) 
                    
                    self._add_display_field(parent_for_fields, display_label_for_field, value_from_item,
                                            section_id_for_edit=section_id, 
                                            item_index_for_edit=item_index, 
                                            json_key_for_edit=json_key_from_item, # Pass English JSON key
                                            is_multiline=is_multiline_display)
        
        self.display_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def get_html_section_definition(self, section_id_to_find: str) -> Optional[Dict[str,Any]]:
        """
        Placeholder/Helper to get the HTML tool's section definition.
        In a real app, this data (similar to sectionTypeData from HTML)
        would be loaded or defined within this Python application to map
        JSON keys back to user-friendly English labels for display.
        """
        # This is a simplified mock. You'd need the full sectionTypeData here
        # or a way to derive labels from the loaded UCPProfile library if it stored them.
        mock_section_type_data_for_labels = {
            "personal": {"fields": [
                {"jsonKey": "preferredName", "label": "Preferred Name"},
                {"jsonKey": "dateOfBirth", "label": "Date of Birth"},
                {"jsonKey": "nationalityCulturalBackground", "label": "Nationality/Cultural Background"},
                {"jsonKey": "languagesProficiency", "label": "Languages Proficiency"}
            ]},
            "social": {"fields": [{"jsonKey": "socialFamilyDetails", "label": "Social & Family Details"}]},
            "educational_professional": {"fields": [
                {"jsonKey": "educationalBackground", "label": "Educational Background"},
                {"jsonKey": "professionalExperience", "label": "Professional Experience"}
            ]},
            "thinking_reference": {"fields": [
                {"jsonKey": "coreThinkingReferenceDescription", "label": "Core Thinking Reference Description"},
                {"jsonKey": "thinkingReferenceApplication", "label": "Thinking Reference Application"}
            ]},
            "ethical_values": {"fields": [
                {"jsonKey": "ethicalValueName", "label": "Ethical Value Name"},
                {"jsonKey": "ethicalValueExplanation", "label": "Ethical Value Explanation"}
            ]},
            "projects": {"fields": [
                {"jsonKey": "projectOrObjectiveTitle", "label": "Project/Objective Title"},
                {"jsonKey": "projectGoals", "label": "Project Goals"}, # Example
                {"jsonKey": "projectLLMRole", "label": "LLM Role in Project"} # Example
            ]},
            "role": {"fields": [
                {"jsonKey": "llmPrimaryRole", "label": "LLM Primary Role"},
                {"jsonKey": "llmRoleAttributes", "label": "LLM Role Attributes"}
            ]},
            "conceptual_tuning": {"fields": [
                {"jsonKey": "userSpecificTerm", "label": "User Specific Term"},
                {"jsonKey": "userTermDefinition", "label": "User Term Definition"}
            ]},
            "intervention_level": {"fields": [
                {"jsonKey": "chosenInterventionLevel", "label": "Chosen Intervention Level"},
                {"jsonKey": "interventionClarifications", "label": "Intervention Clarifications"}
            ]},
            # ... YOU MUST COMPLETE THIS MOCK WITH ALL 25 SECTION DEFINITIONS AND THEIR FIELDS/JSONKEYS/LABELS
            # AS DEFINED IN YOUR HTML TOOL's sectionTypeData
            "alignment_level": {"fields": [{"jsonKey": "desiredAlignmentLevel", "label":"Desired Alignment Level"}, {"jsonKey": "alignmentLevelNotes", "label":"Alignment Notes"}]},
            "mental_state": {"fields": [{"jsonKey": "selectedMentalState", "label":"Selected Mental State"}, {"jsonKey": "mentalStateNotes", "label":"Mental State Notes"}]},
            "sports_inclinations": {"fields": [{"jsonKey": "chosenSportInclination", "label":"Sport Inclination"}, {"jsonKey": "sportOtherDetails", "label":"Sport Other Details"}]},

        }
        return mock_section_type_data_for_labels.get(section_id_to_find)


    def export_as_formatted_text(self):
        if not self.loaded_ucp_data or not self.ucp_profile_loader: # <--- السطر الصحيح
             messagebox.showwarning("No File Loaded", "Please load a UCP-LLM protocol file first.", parent=self.master)
             return
        
        output_lines = [f"## User Context Protocol (UCP-LLM) - Exported by Profile Manager v1.0.0"]
        output_lines.append(f"**Original Tool Version (that created the JSON):** {self.ucp_profile_loader.get_generator_tool_version() or 'N/A'}")
        output_lines.append(f"**Original Generation Date:** {self.ucp_profile_loader.get_generation_date() or 'N/A'}")
        output_lines.append("\n---\n")
        
        section_counter = 1
        # Iterate through the sections in the order they appear in the loaded JSON
        for section_data_from_json in self.loaded_ucp_data.get("sections", []):
            section_id = section_data_from_json.get("id")
            # Use the English title directly from the JSON section data for the text export header
            section_display_title_from_json = section_data_from_json.get("title", f"Section ID: {section_id}")
            if not section_id: continue

            output_lines.append(f"### {section_counter}. Section: {section_display_title_from_json}")
            
            items_to_export = section_data_from_json.get("items", [])
            if not items_to_export:
                 output_lines.append("    (This section is empty in the current data)")
            
            for item_index, item_data_dict in enumerate(items_to_export):
                if len(items_to_export) > 1:
                    output_lines.append(f"  #### Item ({item_index + 1}):")
                
                # To get display labels for text export, refer to HTML definition
                html_section_def = self.get_html_section_definition(section_id)

                for json_key, value in item_data_dict.items():
                    display_label_for_text = json_key # Default to jsonKey
                    if html_section_def:
                        field_def = next((f for f in html_section_def.get("fields", []) if f.get("jsonKey") == json_key), None)
                        if field_def:
                            display_label_for_text = field_def.get("label", json_key) # Use HTML label

                    value_str = str(value)
                    if "\n" in value_str: # Handle multiline values nicely
                        output_lines.append(f"    - **{display_label_for_text}:**")
                        for line_idx, line in enumerate(value_str.splitlines()):
                            output_lines.append(f"      {line.strip()}")
                    else:
                        output_lines.append(f"    - **{display_label_for_text}:** {value_str}")
            output_lines.append("") 
            section_counter +=1
        
        output_lines.append("\n---\n")
        output_lines.append("This text export was generated by UCP-LLM Profile Manager v1.0.0.")
        content_to_export = "\n".join(output_lines)

        try:
            user_identifier_for_filename = self.ucp_profile_loader.get_personal_preferred_name() or "Profile"
            initial_filename = f"UCP-LLM_TextExport_{user_identifier_for_filename.replace(' ', '_')}_v1.0.0.txt"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Formatted Protocol Text", initialfile=initial_filename )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content_to_export)
                messagebox.showinfo("Success", f"Protocol text exported successfully to:\n{filepath}", parent=self.master)
            else: self._update_status("Text export cancelled.")
        except Exception as e: 
            messagebox.showerror("Text Export Error", f"An error occurred: {str(e)}", parent=self.master)

def main():
    root = tk.Tk()
    app = UCPManagerApp(root) 
    root.mainloop()

if __name__ == "__main__":
    main()
