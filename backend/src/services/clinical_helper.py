class ClinicalResponseHelper:
    """Generates structured, clinically grounded crisis response draft templates for operators."""

    # Gentle, validating reflections of each cognitive-distortion pattern (Beck/Burns
    # taxonomy) for use in draft responses. Deliberately non-clinical, non-diagnostic
    # language -- naming a pattern as a "cognitive distortion" to the person experiencing
    # it would read as judgmental and violates the "validate without diagnosing" guideline,
    # so these reflect the pattern back supportively instead of labeling it.
    DISTORTION_REFLECTIONS = {
        "All-or-Nothing Thinking": (
            "It sounds like things feel like a total win or a total loss right now, with no "
            "in-between -- that feeling is real, even if it doesn't always match what's actually true."
        ),
        "Overgeneralization": (
            "It sounds like this pain feels like it's 'always' there or 'never' going to change -- "
            "but one hard stretch doesn't define every moment that comes after it."
        ),
        "Mental Filter": (
            "It sounds like the hard parts are taking up all the space in your mind right now, "
            "making it hard to notice anything else."
        ),
        "Disqualifying the Positive": (
            "It sounds like you might be brushing off anything good that happens, like it doesn't "
            "really count -- but it does."
        ),
        "Jumping to Conclusions": (
            "It sounds like you're carrying a lot of certainty about how this will turn out, or what "
            "others are thinking -- even though none of us can really know that for sure."
        ),
        "Magnification / Catastrophizing": (
            "It sounds like this feels completely overwhelming right now, like nothing could possibly "
            "be okay again -- that intensity is real, even if it can shift with support."
        ),
        "Emotional Reasoning": (
            "It sounds like how strongly you feel something right now is making it feel like proof "
            "that it's true -- but painful feelings, as real as they are, aren't always the full picture."
        ),
        "Should Statements": (
            "It sounds like you're holding yourself to a really strict standard of how things "
            "'should' have gone -- that's a heavy weight to carry."
        ),
        "Labeling": (
            "It sounds like you're using some really harsh words to describe yourself right now -- "
            "you are more than any one hard moment."
        ),
        "Personalization": (
            "It sounds like you're taking on a lot of blame for this -- but rarely is something "
            "entirely one person's fault."
        ),
    }

    @staticmethod
    def get_clinical_guidelines():
        return {
            "principles": [
                "De-escalate emotional intensity using active listening.",
                "Validate emotional pain without judging or diagnosing.",
                "Encourage the user to explore professional human support channels.",
                "Never suggest specific medications, clinical conditions, or therapies.",
                "Provide clear, immediate crisis contact information."
            ]
        }

    def _distortion_reflection(self, dominant_distortions):
        """Returns a reflective sentence for the top-ranked detected distortion, or ''."""
        if not dominant_distortions:
            return ""
        reflection = self.DISTORTION_REFLECTIONS.get(dominant_distortions[0])
        return f" {reflection}" if reflection else ""

    def generate_draft(self, tier, dominant_emotion, text_snippet=None, dominant_distortions=None):
        """
        Generates a helper draft response according to safety guidelines. When
        dominant_distortions (from cognitive_distortion_analyzer.get_dominant_distortions)
        is provided, the top-ranked pattern is gently reflected back into the draft.
        """
        guidelines = self.get_clinical_guidelines()["principles"]
        distortion_note = self._distortion_reflection(dominant_distortions)

        # 1. Tier 0: No Risk
        if tier == 0:
            return {
                "draft": (
                    "Thank you for sharing your thoughts. It sounds like you are going through a normal day, "
                    "but if you ever need someone to talk to or additional resources, we are always here to support you. "
                    "Take care."
                ),
                "guidelines": [guidelines[2], guidelines[3]]
            }

        # 2. Tier 1: Mild Distress
        if tier == 1:
            emotion_mapping = {
                "sadness": "it sounds like you are feeling really down and lonely right now.",
                "anxiety": "I hear how stressed and overwhelmed you are feeling about everything.",
                "anger": "I can feel how frustrating and exhausting this situation must be for you."
            }
            context = emotion_mapping.get(dominant_emotion.lower(), "I hear that you're going through a challenging moment.")

            return {
                "draft": (
                    f"Thank you for reaching out and sharing this. {context}{distortion_note} Please know that your feelings are valid, "
                    "and you don't have to carry this stress alone. Sometimes talking to someone you trust, like a friend, "
                    "family member, or counselor, can help ease the burden. We are here to support you, and we encourage "
                    "you to take things one step at a time."
                ),
                "guidelines": [guidelines[0], guidelines[1], guidelines[2]]
            }

        # 3. Tier 2: Moderate Risk (Passive Ideation)
        if tier == 2:
            return {
                "draft": (
                    "I am so sorry you are going through such a painful and difficult time right now. Please know that "
                    f"I hear you, and your life and feelings are important.{distortion_note} When pain feels overwhelming, it can be really "
                    "helpful to speak with someone trained to listen and support you. You can reach out to the Suicide & "
                    "Crisis Lifeline by calling or texting 988. It is free, confidential, and available 24/7. "
                    "Please consider connecting with them or reaching out to a professional who can help support you through this."
                ),
                "guidelines": [guidelines[0], guidelines[1], guidelines[2], guidelines[4]]
            }

        # 4. Tier 3: Severe Active Risk
        if tier == 3:
            return {
                "draft": (
                    f"I hear how much pain you are in, and I want to support you.{distortion_note} You do not have to go through this alone. "
                    "Please connect with immediate help right now. You can call or text the Suicide & Crisis Lifeline "
                    "at 988 (free, confidential, and available 24/7 in the US). If you are outside the US, please "
                    "go to your nearest emergency room or contact your local emergency services immediately. "
                    "There are people who want to listen and help you stay safe tonight. Please reach out to them."
                ),
                "guidelines": [guidelines[0], guidelines[2], guidelines[4]]
            }

if __name__ == "__main__":
    helper = ClinicalResponseHelper()
    res = helper.generate_draft(2, "sadness", dominant_distortions=["Personalization"])
    print("Draft Response (Tier 2):")
    print(res["draft"])
    print("\nApplied Guidelines:")
    print(res["guidelines"])
