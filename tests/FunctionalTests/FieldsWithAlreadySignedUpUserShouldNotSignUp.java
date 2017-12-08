package com.example.tests;

import java.util.regex.Pattern;
import java.util.concurrent.TimeUnit;
import org.junit.*;
import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;
import org.openqa.selenium.*;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.Select;

public class FieldsWithAlreadySignedUpUserShouldNotSignUp {
  private WebDriver driver;
  private String baseUrl;
  private boolean acceptNextAlert = true;
  private StringBuffer verificationErrors = new StringBuffer();

  @Before
  public void setUp() throws Exception {
    driver = new FirefoxDriver();
    baseUrl = "https://www.katalon.com/";
    driver.manage().timeouts().implicitlyWait(30, TimeUnit.SECONDS);
  }

  @Test
  public void testFieldsWithAlreadySignedUpUserShouldNotSignUp() throws Exception {
    driver.get("http://localhost:5000/signup");
    driver.findElement(By.id("username")).clear();
    driver.findElement(By.id("username")).sendKeys("testuser");
    driver.findElement(By.id("name")).clear();
    driver.findElement(By.id("name")).sendKeys("Test User");
    driver.findElement(By.id("email")).clear();
    driver.findElement(By.id("email")).sendKeys("mky515@gmail.com");
    driver.findElement(By.id("phone")).clear();
    driver.findElement(By.id("phone")).sendKeys("5554443322");
    driver.findElement(By.id("password")).clear();
    driver.findElement(By.id("password")).sendKeys("1234");
    driver.findElement(By.id("confirm")).clear();
    driver.findElement(By.id("confirm")).sendKeys("1234");
    driver.findElement(By.id("accept_terms")).click();
    driver.findElement(By.xpath("//input[@value='Sign Up']")).click();
    // Warning: assertTextPresent may require manual changes
    assertTrue(driver.findElement(By.cssSelector("BODY")).getText().matches("^[\\s\\S]*Already signed up user![\\s\\S]*$"));
  }

  @After
  public void tearDown() throws Exception {
    driver.quit();
    String verificationErrorString = verificationErrors.toString();
    if (!"".equals(verificationErrorString)) {
      fail(verificationErrorString);
    }
  }

  private boolean isElementPresent(By by) {
    try {
      driver.findElement(by);
      return true;
    } catch (NoSuchElementException e) {
      return false;
    }
  }

  private boolean isAlertPresent() {
    try {
      driver.switchTo().alert();
      return true;
    } catch (NoAlertPresentException e) {
      return false;
    }
  }

  private String closeAlertAndGetItsText() {
    try {
      Alert alert = driver.switchTo().alert();
      String alertText = alert.getText();
      if (acceptNextAlert) {
        alert.accept();
      } else {
        alert.dismiss();
      }
      return alertText;
    } finally {
      acceptNextAlert = true;
    }
  }
}
