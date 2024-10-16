#coding: utf-8    

import smtplib
from email.mime.image import MIMEImage
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notifier_Email():

    @staticmethod
    def notify(title: str, content: str, target_user: str, **kwargs) -> str:
        
        result = Notifier_Email.send_email_163(title=title, content=content, target_user=target_user)

        return "OK"
    
    @staticmethod
    def send_email_163(title: str, content: str, target_user: str, **kwargs):
        try:
            #下面的发件人，收件人是用于邮件传输的。
            smtpserver = 'smtp.163.com'
            username = 'roarhill@163.com'
            password = 'Mthgh666'
            sender='roarhill@163.com'

            #receiver='XXX@126.com'
            #收件人为多个收件人
            receiver=['roarson2024@163.com','roar2024@163.com']

            subject = title
            #通过Header对象编码的文本，包含utf-8编码信息和Base64编码信息。以下中文名测试ok
            #subject = '中文标题'
            #subject=Header(subject, 'utf-8').encode()

            #构造邮件对象MIMEMultipart对象
            #下面的主题，发件人，收件人，日期是显示在邮件页面上的。
            msg = MIMEMultipart('mixed') 
            msg['Subject'] = subject
            msg['From'] = 'OddMeta <roarhill@163.com>'
            #msg['To'] = 'XXX@126.com'
            #收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
            msg['To'] = ";".join(receiver) 
            #msg['Date']='2012-3-16'

            #构造文字内容
            text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.baidu.com"
            text_plain = MIMEText(text,'plain', 'utf-8')
            msg.attach(text_plain)

            #构造图片链接
            sendimagefile=open(r'g:\\mark.png','rb').read()
            image = MIMEImage(sendimagefile)
            image.add_header('Content-ID','<image1>')
            image["Content-Disposition"] = 'attachment; filename="mark.png"'
            msg.attach(image)

            #构造html
            #发送正文中的图片:由于包含未被许可的信息，网易邮箱定义为垃圾邮件，报554 DT:SPM ：<p><img src="cid:image1"></p>
            html = """
            <html>
            <head></head>
            <body>
                <p>Hi!<br>
                How are you?<br>
                Here is the <a href="http://www.baidu.com">link</a> you wanted.<br>
                </p>
            </body>
            </html>
            """
            text_html = MIMEText(html,'html', 'utf-8')
            text_html["Content-Disposition"] = 'attachment; filename="texthtml.html"'
            msg.attach(text_html)

            #构造附件
            sendfile=open(r'g:\\ban.txt','rb').read()
            text_att = MIMEText(sendfile, 'base64', 'utf-8')
            text_att["Content-Type"] = 'application/octet-stream'
            #以下附件可以重命名成aaa.txt
            #text_att["Content-Disposition"] = 'attachment; filename="aaa.txt"'
            #另一种实现方式
            text_att.add_header('Content-Disposition', 'attachment', filename='aaa.txt')
            #以下中文测试不ok
            #text_att["Content-Disposition"] = u'attachment; filename="中文附件.txt"'.decode('utf-8')
            msg.attach(text_att)
                
            #发送邮件
            smtp = smtplib.SMTP()
            smtp.connect('smtp.163.com')
            #我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
            #smtp.set_debuglevel(1)
            smtp.login(username, password)
            smtp.sendmail(sender, receiver, msg.as_string())
            smtp.quit()
        except Exception as e:
            print(f"send email failed: {str(e)}")

    def send_mail_gmail(text: str, target_user: str, **kwargs):
        # 邮件发送者和接收者
        sender_email = "jackyhwei1@gmail.com"
        receiver_email = "jacky@rg4.net"
        
        # 创建邮件对象和设置邮件内容
        message = MIMEMultipart("alternative")
        message["Subject"] = "Email Subject"
        message["From"] = sender_email
        message["To"] = receiver_email
 
        # 创建邮件正文
        text = """\
        This is an example email body.
        It can be in HTML or plain text.
        """
        html = """\
        <html>
        <body>
            <p>This is an example email body.</p>
            <p>It can be in HTML or plain text.</p>
        </body>
        </html>
        """
        # 添加文本和HTML的部分
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        # 添加正文到邮件对象中
        message.attach(part1)
        message.attach(part2)
        
        # 发送邮件
        try:
            # 创建SMTP服务器连接
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                # 登录到邮件服务器
                server.login(sender_email, "your_password")
                # 发送邮件
                server.sendmail(sender_email, receiver_email, message.as_string())
        except Exception as e:
            print(f"Error: {e}")
        else:
            print("Email sent successfully!")

        return "OK"
