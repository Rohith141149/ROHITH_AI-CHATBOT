import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import Home from "../page";

// Mock fetch globally
global.fetch = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
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
    it("opens the chat window when toggle button is clicked", () => {
      render(<Home />);
      const toggleBtn = screen.getByRole("button", { name: /open chat/i });
      fireEvent.click(toggleBtn);
      expect(screen.getByText("Rohith AI Assistant")).toBeInTheDocument();
    });

    it("closes the chat window when close button is clicked", () => {
      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      expect(screen.getByText("Rohith AI Assistant")).toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: /close chat/i }));
      expect(screen.queryByText("Rohith AI Assistant")).not.toBeInTheDocument();
    });

    it("shows placeholder text when chat is open and empty", () => {
      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));
      expect(screen.getByText(/ask me anything/i)).toBeInTheDocument();
    });
  });

  describe("Sending messages", () => {
    it("sends a message and shows user bubble", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: "AI reply" }),
      });

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(screen.getByText("Hello")).toBeInTheDocument();
    });

    it("shows AI response after sending message", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: "AI reply" }),
      });

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

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
      global.fetch.mockRejectedValueOnce(new Error("Failed to fetch"));

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      await waitFor(() => {
        expect(
          screen.getByText(/unable to connect to backend/i)
        ).toBeInTheDocument();
      });
    });

    it("clears input after sending", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: "reply" }),
      });

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(input.value).toBe("");
    });

    it("does not send empty messages", () => {
      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);
      fireEvent.change(input, { target: { value: "   " } });
      fireEvent.click(screen.getByRole("button", { name: /send/i }));

      expect(global.fetch).not.toHaveBeenCalled();
    });

    it("sends message on Enter key press", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: "reply" }),
      });

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.keyDown(input, { key: "Enter" });
      });

      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe("Clear chat", () => {
    it("clears all messages when clear button is clicked", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ response: "AI reply" }),
      });

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

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
      let resolvePromise;
      global.fetch.mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
      );

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      expect(screen.getByText(/typing/i)).toBeInTheDocument();

      await act(async () => {
        resolvePromise({ ok: true, json: async () => ({ response: "Done" }) });
      });
    });

    it("disables send button while loading", async () => {
      let resolvePromise;
      global.fetch.mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
      );

      render(<Home />);
      fireEvent.click(screen.getByRole("button", { name: /open chat/i }));

      const input = screen.getByPlaceholderText(/type your message/i);

      await act(async () => {
        fireEvent.change(input, { target: { value: "Hello" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));
      });

      const sendBtn = screen.getByRole("button", { name: /send/i });
      expect(sendBtn).toBeDisabled();

      await act(async () => {
        resolvePromise({ ok: true, json: async () => ({ response: "Done" }) });
      });
    });
  });
});
