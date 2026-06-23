// Mock scrollIntoView since jsdom doesn't support it
Element.prototype.scrollIntoView = jest.fn();
