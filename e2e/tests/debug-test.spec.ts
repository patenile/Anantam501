import { test, expect } from "@playwright/test";

test("debug registration", async ({ page }) => {
  // Listen for console messages
  page.on("console", (msg) => console.log("BROWSER LOG:", msg.text()));

  await page.goto("/", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForSelector("text=Register", { timeout: 10000 });
  await page.click("text=Register"); // Click nav button to show form

  await page.fill('input[placeholder="Email"]', "test@test.com");
  await page.fill('input[placeholder="Password"]', "password123");
  await page.fill('input[placeholder="Full Name"]', "Test User");

  console.log("About to click Register submit button...");
  await page.getByTestId("register-submit-button").click();

  // Wait a bit to see console logs
  await page.waitForTimeout(2000);

  // Check what the message div contains
  const messageDiv = await page.getByTestId("registration-message");
  const text = await messageDiv.textContent();
  const isVisible = await messageDiv.isVisible();

  console.log("Message div text:", text);
  console.log("Message div visible:", isVisible);
});
