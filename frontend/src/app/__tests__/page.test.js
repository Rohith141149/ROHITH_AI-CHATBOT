import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import Home from "../page";

// Mock fetch globally with URL-aware responses
global.fetch = jest.fn();

function mockFetch(chatResponse) {
  global.fetch.mockImplementation((url, options) => {
    // Health check (GET /)
    if (!options || options.method === "GET" || url.endsWith("/")) {
      return Promise.resolve({ ok: true, json: async () => ({ message: "ok" }) });
    }
    // Chat endpoint
    if (chatResponse instanceof Error) {
      return Promise.reject(chatResponse);
    }
    return Promise.resolve({
      ok: true,
      json: async () => chatResponse,
    });
  });
}

function mockFetchOffline() {
  global.fetch.mockImplementation(() => {
    return Promise.reject(new Error("Network error"));
  });
}

beforeEach(() => {
  jest.clearAllMocks();
  // Default: health check succeeds, chat not mocked
  mockFetch({ response: "default reply" });
});

describe("Home (ChatWidget)", () => {
  describe("Initial render", () => {
    it("renders the chat toggle button", () => {
      render(<Home />);
      const toggleBtn = screen.getByRole("button", { name: /open chat/i });
      expect(toggleBtn).toBeInTheDocument();
    });

    it("chat window is closed by default", () => {
      render(<Home />);
      expect(screen.queryByText("Rohith AI Assistant")).not.toBeInTheDocument();
    });
  });

  describe("Chat widget toggle", () => {
    it("opens the chat window when toggle button is clicked", async () => {
      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });
      expect(screen.getByText("Rohith AI Assistant")).toBeInTheDocument();
    });

    it("closes the chat window when close button is clicked", async () => {
      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });
      expect(screen.getByText("Rohith AI Assistant")).toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: /close chat/i }));
      expect(screen.queryByText("Rohith AI Assistant")).not.toBeInTheDocument();
    });

    it("shows placeholder text when chat is open and empty", async () => {
      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });
      expect(screen.getByText(/ask me anything/i)).toBeInTheDocument();
    });
  });

  describe("Sending messages", () => {
    it("sends a message and shows user bubble", async () => {
      mockFetch({ response: "AI reply" });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(screen.getByText("Hello")).toBeInTheDocument();
    });

    it("shows AI response after sending message", async () => {
      mockFetch({ response: "AI reply" });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      await waitFor(() => {
        expect(screen.getByText("AI reply")).toBeInTheDocument();
      });
    });

    it("shows error message when fetch fails", async () => {
      mockFetchOffline();

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      await waitFor(() => {
        expect(
          screen.getByText(/could not reach the server/i)
        ).toBeInTheDocument();
      });
    });

    it("clears input after sending", async () => {
      mockFetch({ response: "reply" });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(input.value).toBe("");
    });

    it("does not send empty messages", async () => {
      const fetchCalls = [];
      global.fetch.mockImplementation((url, options) => {
        fetchCalls.push({ url, options });
        return Promise.resolve({ ok: true, json: async () => ({ message: "ok" }) });
      });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const healthCheckCount = fetchCalls.length;

      const input = screen.getByPlaceholderText(/type your message/i);
      fireEvent.change(input, { target: { value: "   " } });
      fireEvent.click(screen.getByRole("button", { name: /send/i }));

      // No additional fetch calls beyond the health check
      expect(fetchCalls.length).toBe(healthCheckCount);
    });

    it("sends message on Enter key press", async () => {
      const fetchCalls = [];
      global.fetch.mockImplementation((url, options) => {
        fetchCalls.push({ url, options });
        return Promise.resolve({ ok: true, json: async () => ({ response: "reply" }) });
      });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const healthCheckCount = fetchCalls.length;

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.keyDown(input, { key: "Enter" });
      });

      // Additional fetch call made for the chat message
      expect(fetchCalls.length).toBeGreaterThan(healthCheckCount);
    });
  });

  describe("Clear chat", () => {
    it("clears all messages when clear button is clicked", async () => {
      mockFetch({ response: "AI reply" });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      await waitFor(() => {
        expect(screen.getByText("AI reply")).toBeInTheDocument();
      });

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /clear/i }));
      });

      expect(screen.queryByText("Hello")).not.toBeInTheDocument();
      expect(screen.queryByText("AI reply")).not.toBeInTheDocument();
    });
  });

  describe("Loading state", () => {
    it("shows typing indicator while waiting for response", async () => {
      let resolveChat;
      global.fetch.mockImplementation((url, options) => {
        if (!options || options.method === "GET" || url.endsWith("/")) {
          return Promise.resolve({ ok: true, json: async () => ({ message: "ok" }) });
        }
        return new Promise((resolve) => {
          resolveChat = resolve;
        });
      });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(screen.getByText(/typing/i)).toBeInTheDocument();

      await act(async () => {
        resolveChat({ ok: true, json: async () => ({ response: "Done" }) });
      });
    });

    it("disables send button while loading", async () => {
      let resolveChat;
      global.fetch.mockImplementation((url, options) => {
        if (!options || options.method === "GET" || url.endsWith("/")) {
          return Promise.resolve({ ok: true, json: async () => ({ message: "ok" }) });
        }
        return new Promise((resolve) => {
          resolveChat = resolve;
        });
      });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      const sendBtn = screen.getByRole("button", { name: /send/i });
      expect(sendBtn).toBeDisabled();

      await act(async () => {
        resolveChat({ ok: true, json: async () => ({ response: "Done" }) });
      });
    });
  });

  describe("Backend status", () => {
    it("shows Online status when backend is reachable", async () => {
      mockFetch({ response: "reply" });

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      await waitFor(() => {
        expect(screen.getByText("Online")).toBeInTheDocument();
      });
    });

    it("shows Offline status when backend is unreachable", async () => {
      mockFetchOffline();

      render(<Home />);
      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      });

      await waitFor(() => {
        expect(screen.getByText(/offline/i)).toBeInTheDocument();
      });
    });
  });
});
