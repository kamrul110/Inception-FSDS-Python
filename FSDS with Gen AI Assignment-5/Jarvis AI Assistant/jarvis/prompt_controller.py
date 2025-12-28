
class PromptController:
    def _system_instructions(self, role: str) -> str:
        """Return system-level instructions/persona based on the selected role."""
        base = (
            "You are JARVIS, a friendly and highly capable personal AI assistant. "
            "Always be clear, concise, and encouraging."
        )

        role = (role or "Tutor").lower()
        if role == "coder":
            spec = (
                "You are acting as a coding assistant. Explain code in simple terms, "
                "suggest improvements, and provide Python examples when helpful."
            )
        elif role == "mentor":
            spec = (
                "You are acting as a career mentor. Give practical advice about "
                "learning paths, interviews, and career growth in tech."
            )
        else:  # tutor (default)
            spec = (
                "You are acting as a tutor. Break down complex topics into simple "
                "steps and check the student's understanding."
            )

        return base + " " + spec

    def build_prompt(self, user_input, memory, role: str):
        """Build the full prompt with system instructions, history, and new input."""
        context = "\n".join([f"{m['role']}: {m['message']}" for m in memory])
        system = self._system_instructions(role)
        prompt = f"System: {system}\n\nConversation so far:\n{context}\nUser: {user_input}\nAssistant:"
        return prompt
