it("handles navigation edge cases and state reset", () => {
  render(<App />);
  // Switch to register, fill fields, then switch to login and back
  fireEvent.click(screen.getByText(/register/i));
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "edge@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "edgepass" },
  });
  fireEvent.change(screen.getByPlaceholderText(/full name/i), {
    target: { value: "Edge Case" },
  });
  fireEvent.click(screen.getByText(/login/i));
  expect(screen.getByRole("heading", { name: /login/i })).toBeInTheDocument();
  // Go back to register, fields should persist (since state is not reset)
  fireEvent.click(screen.getByText(/register/i));
  expect(screen.getByDisplayValue("edge@example.com")).toBeInTheDocument();
  expect(screen.getByDisplayValue("edgepass")).toBeInTheDocument();
  expect(screen.getByDisplayValue("Edge Case")).toBeInTheDocument();
});

it("trims whitespace in registration and login", () => {
  render(<App />);
  fireEvent.click(screen.getByText(/register/i));
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "   spaced@example.com   " },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "   spacedpass   " },
  });
  fireEvent.change(screen.getByPlaceholderText(/full name/i), {
    target: { value: "   Spaced User   " },
  });
  fireEvent.click(screen.getByTestId("register-submit-button"));
  expect(screen.getByTestId("registration-message")).toHaveTextContent(
    /registration successful/i,
  );

  // Now login with trimmed values
  fireEvent.click(screen.getByText(/login/i));
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "spaced@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "spacedpass" },
  });
  fireEvent.click(screen.getByTestId("login-submit-button"));
  expect(
    screen.getByRole("heading", { name: /welcome, spaced user/i }),
  ).toBeInTheDocument();
});

it("handles rapid view switching without breaking state", () => {
  render(<App />);
  for (let i = 0; i < 5; i++) {
    fireEvent.click(screen.getByText(/register/i));
    fireEvent.click(screen.getByText(/login/i));
  }
  expect(screen.getByRole("heading", { name: /login/i })).toBeInTheDocument();
  fireEvent.click(screen.getByText(/register/i));
  expect(
    screen.getByRole("heading", { name: /register/i }),
  ).toBeInTheDocument();
});

it("persists registration state across multiple logins", () => {
  render(<App />);
  fireEvent.click(screen.getByText(/register/i));
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "multi@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "multipass" },
  });
  fireEvent.change(screen.getByPlaceholderText(/full name/i), {
    target: { value: "Multi User" },
  });
  fireEvent.click(screen.getByTestId("register-submit-button"));
  fireEvent.click(screen.getByText(/login/i));
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "multi@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "multipass" },
  });
  fireEvent.click(screen.getByTestId("login-submit-button"));
  expect(
    screen.getByRole("heading", { name: /welcome, multi user/i }),
  ).toBeInTheDocument();
  // Logout and login again
  fireEvent.click(screen.getByText(/logout/i));
  fireEvent.click(screen.getAllByText(/^login$/i)[0]); // Click the navigation Login button
  fireEvent.change(screen.getByPlaceholderText(/email/i), {
    target: { value: "multi@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText(/password/i), {
    target: { value: "multipass" },
  });
  fireEvent.click(screen.getByTestId("login-submit-button"));
  expect(
    screen.getByRole("heading", { name: /welcome, multi user/i }),
  ).toBeInTheDocument();
});

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";
import { describe, it, expect } from "vitest";
import "@testing-library/jest-dom";

describe("App", () => {
  it("renders the main heading", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: /welcome to anantam/i }),
    ).toBeInTheDocument();
  });

  it("can switch to register view and validate registration", () => {
    render(<App />);
    fireEvent.click(screen.getByText(/register/i));
    expect(
      screen.getByRole("heading", { name: /register/i }),
    ).toBeInTheDocument();

    // Try invalid email
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "not-an-email" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "pass1234" },
    });
    fireEvent.change(screen.getByPlaceholderText(/full name/i), {
      target: { value: "Test User" },
    });
    fireEvent.click(screen.getByTestId("register-submit-button"));
    expect(screen.getByTestId("registration-message")).toHaveTextContent(
      /invalid email/i,
    );

    // Try missing fields
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "" },
    });
    fireEvent.click(screen.getByTestId("register-submit-button"));
    expect(screen.getByTestId("registration-message")).toHaveTextContent(
      /all fields required/i,
    );

    // Valid registration
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "pass1234" },
    });
    fireEvent.change(screen.getByPlaceholderText(/full name/i), {
      target: { value: "Test User" },
    });
    fireEvent.click(screen.getByTestId("register-submit-button"));
    expect(screen.getByTestId("registration-message")).toHaveTextContent(
      /registration successful/i,
    );
  });

  it("can switch to login view and handle login logic", () => {
    render(<App />);
    // Register first
    fireEvent.click(screen.getByText(/register/i));
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "pass1234" },
    });
    fireEvent.change(screen.getByPlaceholderText(/full name/i), {
      target: { value: "Test User" },
    });
    fireEvent.click(screen.getByTestId("register-submit-button"));

    // Switch to login
    fireEvent.click(screen.getByText(/login/i));
    expect(screen.getByRole("heading", { name: /login/i })).toBeInTheDocument();

    // Wrong credentials
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "wrong@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByTestId("login-submit-button"));
    expect(screen.getByTestId("login-message")).toHaveTextContent(
      /invalid credentials/i,
    );

    // Correct credentials
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "pass1234" },
    });
    fireEvent.click(screen.getByTestId("login-submit-button"));
    expect(
      screen.getByRole("heading", { name: /welcome, test user/i }),
    ).toBeInTheDocument();
    // Logout
    fireEvent.click(screen.getByText(/logout/i));
    expect(
      screen.getByRole("heading", { name: /welcome to anantam/i }),
    ).toBeInTheDocument();
  });
});
