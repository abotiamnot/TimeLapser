email_path = '/usr/lib/raspiwifi/configuration_app/list_of_emails.txt'

def table_generate(mail_list):
    empty = '''
             <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td></td>
          <td></td>
        </tr>
        <tr>
          <td>Name2</td>
          <td>Description2</td>
        </tr>
        <tr>
          <td>Name3</td>
          <td>Description3</td>
        </tr>
      </tbody>
    </table>
            '''
    head = '<table><thead><tr><th>E-Mail</th><th>Action</th></tr></thead>'
    content = '<tr><td>{}</td><td>{}</td></tr>'
    body = []
    for a,b in enumerate(mail_list):
        body.append(content.format(b, '<button name="delete" type="submit" value="{}">Delete</button>'.format(str(a))))
    body_ = ''.join(body)
    end = '</tbody></table><br><input type="text" name="email_" id="email_"><button name="email" type="submit" value="{}">Submit</button>'
    entire_html = '{}{}{}'.format(head, body_, end)
    new_list = ','.join(mail_list)
    with open(email_path, 'w') as f:
            f.write(new_list)
    return entire_html

def email_extractor():
        file_ = open(email_path, 'r')
        content_ = file_.read()
        file_.close()
        return content_.split(',')
