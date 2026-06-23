export function createUserMessage(text) {
  return { role: "user", text };
}

export function createAssistantMessage(text) {
  return { role: "assistant", text };
}

export function toConversationHistory(messages) {
  return messages.map((msg) => ({
    role: msg.role === "assistant" ? "assistant" : "user",
    content: msg.text,
  }));
}
