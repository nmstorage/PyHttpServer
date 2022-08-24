from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import sys
import pyodbc 

DATABASE = 'Sales' 
USERNAME = 'SalesLogin' 
PASSWORD = '123' 

class MyHTTPServer:
   def __init__(self, host, port):
      self._host = host
      self._port = port
  
   def serve_forever(self):
      httpd = HTTPServer((self._host, self._port), MyHTTPRequestHandler)
      httpd.serve_forever()
    
class MyHTTPRequestHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      # content_length = int(self.headers['Content-Length'])
      # body = self.rfile.read(content_length)
      # self.wfile.write(b'GET request. Received: ')
      # self.wfile.write(body)
      
      server = 'localhost'
      conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};'
         'SERVER='+server+';DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
      cursor = conn.cursor()
      cursor.execute("""SELECT Convert(nVarChar, sDate, 104) as fDate,
         Replace(sVolume, '.', ',') As Volume FROM Sales..tbl_sales WHERE 
         sDate BETWEEN ? AND ? ORDER BY sDate;""",
         format_sdate(self.query['datefrom'][0]), format_sdate(self.query['dateto'][0]))

      body = 'Суммы за выбранный период:\r\n\r\n'
      row = cursor.fetchone() 
      if row:
         while row: 
            body += f'<i>{row.fDate}</i>     <strong>{row.Volume}</strong>\r\n'
            row = cursor.fetchone()
      else:
         body = 'Записи не найдены.'
         
      self.set_headers_and_body(body)
      
   def do_POST(self):
      # content_length = int(self.headers['Content-Length'])
      # body = self.rfile.read(content_length)
      # self.wfile.write(b'POST request. Received: ')
      # self.wfile.write(body)
      
      server = 'localhost'
      conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};'
         'SERVER='+server+';DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
      cursor = conn.cursor()
      count = cursor.execute("""INSERT INTO Sales..tbl_sales (sVolume, sDate) VALUES (?,?)""",
         self.query['volume'][0].replace(',','.'), format_sdate(self.query['date'][0])).rowcount
      conn.commit()
      
      body = 'Запись сохранена.'
      self.set_headers_and_body(body)
      
   @property
   def url_parts(self):
      return urlparse(self.path)
      
   @property
   def query(self):
      return parse_qs(self.url_parts.query)

   def set_headers_and_body(self, body):
      self.send_response(200)
      body = body.encode('utf-8')
      self.send_header('Content-type', 'text/html; charset=utf-8')
      self.send_header('Content-Length', len(body))
      self.end_headers()
      self.wfile.write(body)


def format_sdate(date_str):
   return date_str[6:]+'-'+date_str[3:5]+'-'+date_str[:2]


if __name__ == '__main__':
   host = sys.argv[1]
   port = int(sys.argv[2])

   serv = MyHTTPServer(host, port)
   try:
      serv.serve_forever()
   except KeyboardInterrupt:
      pass