export function createUserMessage(text) {
  return { role: "user", text };
}

export function createAssistantMessage(text) {
  return { role: "assistant", text };
}

export function createErrorMessage(text) {
  return { role: "assistant", text, isError: true };
}

export function toConversationHistory(messages) {
  return messages
    .filter((msg) => !msg.isError)
    .map((msg) => ({
      role: msg.role === "assistant" ? "assistant" : "user",
      content: msg.text,
    }));
}
