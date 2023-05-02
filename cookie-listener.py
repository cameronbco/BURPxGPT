from burp import IBurpExtender, ITab, IProxyListener
from javax.swing import JPanel, JTabbedPane, JTextArea, JScrollPane, ScrollPaneConstants, JButton
from java.awt import BorderLayout, Dimension
from java.net import URL
from java.io import DataOutputStream, BufferedReader, InputStreamReader, PrintWriter
import json
import os

class BurpExtender(IBurpExtender, ITab, IProxyListener):

  def registerExtenderCallbacks(self, callbacks):
    self._callbacks = callbacks
    self._helpers = callbacks.getHelpers()
    self._stdout = PrintWriter(callbacks.getStdout(), True)
    callbacks.setExtensionName("OpenAI x BURP")
    
    self._extension_tab = ExtensionTab(self._stdout)
    callbacks.addSuiteTab(self)
    callbacks.registerProxyListener(self)
    
  def getTabCaption(self):
    return "Test tab"
    
  def getUiComponent(self):
    return self._extension_tab
  
  def processProxyMessage(self, messageIsRequest, message):
    request_response = message.getMessageInfo()
    request_analysis = self._helpers.analyzeRequest(request_response)
    request_headers = request_analysis.getHeaders()
    
    self._extension_tab.update_text("Request:\n")
    for header in request_headers:
      if (header.startswith("GET") or header.startswith("Cookie") or header.startswith("Host")):
        self._extension_tab.update_text(header + "\n")
    self._extension_tab.update_text("\n")
    
    response_bytes = request_response.getResponse()
    response_analysis = self._helpers.analyzeResponse(response_bytes)
    response_headers = response_analysis.getHeaders()
    
    self._extension_tab.update_text("Response:\n")
    for header in response_headers:
      if (header.startswith("HTTP") or header.startswith("Set-Cookie")):
        self._extension_tab.update_text(header + "\n")
    self._extension_tab.update_text("\n")

class ExtensionTab(JPanel):

  def __init__(self, stdout):
    self._stdout = stdout
    
    self.setLayout(BorderLayout())
    
    config_panel = JPanel()
    self.add(config_panel, BorderLayout.WEST)
    '''
    test_button = JButton("test")
    test_button.setPreferredSize(Dimension(100,25))
    test_button.addActionListener(self.send_openai_request)
    config_panel.add(test_button)
    '''
    
    log_button = JButton("log")
    log_button.setPreferredSize(Dimension(100,25))
    log_button.addActionListener(self.log_text_area)
    config_panel.add(log_button)
    
    self._text_area = JTextArea()
    self._text_area.setEditable(False)
    self._text_area.setLineWrap(True)
    self._text_area.setWrapStyleWord(True)
    
    scroll_pane = JScrollPane(self._text_area)
    scroll_pane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
    self.add(scroll_pane, BorderLayout.CENTER)
    
  def update_text(self, text):
    self._text_area.append(text)
    
  def log_text_area(self, event):
    with open("proxy-dump.txt", "w") as dumpfile:
      proxy_history = self._text_area.getText()
      dumpfile.write(proxy_history)
  
  '''  
  def send_openai_request(self, event):
    API_KEY = "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"
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer {}".format(API_KEY)
    }
    
    data = {
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": "Say this is a test!"}],
      "temperature": 0.7
    }
    
    connection = self.send_post_request(OPENAI_API_URL, headers, json.dumps(data))
    response_code = connection.getResponseCode()
    
    if response_code >=200 and response_code < 300:
      response = self.read_response(connection)
      #self.update_text(response_json)
    else:
      raise Exception("API request failed with response code: {}".format(response_code))
    
  def send_post_request(self, url, headers, data):
    java_url = URL(url)
    connection = java_url.openConnection()
    connection.setDoOutput(True)
    connection.setRequestMethod("POST")
    for key, value in headers.items():
      connection.setRequestProperty(key, value)
      
    output_stream = DataOutputStream(connection.getOutputStream())
    output_stream.writeBytes(data)
    output_stream.flush()
    output_stream.close()
    
    return connection
    
  def read_response(self, connection):
    input_stream = BufferedReader(InputStreamReader(connection.getInputStream()))
    response = ""
    line = input_stream.readLine()
    while line is not None:
      response += line
      line = input_stream.readLine()
    input_stream.close()
    return response
  '''
