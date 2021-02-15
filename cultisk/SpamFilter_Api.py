from flask_restx import Namespace, Resource

import cultisk.Email_Retrieve as ER
from cultisk import app
from cultisk.Models import MainFilter
from cultisk.helper import openid_required, get_openid_identity
import cultisk.MI_model

api = Namespace("spam-filter", description="Email Filter")


@api.route("/spamfilter/")
class MainFilterAPI(Resource):

    @openid_required
    def get(self):
        result_formatted = []
        user_identifier = get_openid_identity()
        # service=ER.return_sevice(user_identifier)
        s_list = []
        p_output = open('cultisk/whitelist.txt', 'r')
        for element in p_output.readlines():
            s_list.append(element.strip())
        p_output.close()
        email_dict = ER.getEmails(user_identifier, s_list)
        count = 1
        new_test = {}
        for i in email_dict:
            email_filtering = MainFilter()
            result = email_filtering.filter(message=email_dict[i][2])
            # print("MessageID: " + str(i))
            # What we have {'messageID': [<Subject>, <Sender>, <body>, <messageID>]
            # What we need is [{<messageID, <body>, <Sender>, <Subject>}]
            if result == 'spam':
                ER.trash_message(user_identifier, i)
                print("Subject:", email_dict[i][0])
                print("Sender:", email_dict[i][1])
                print("Body:", email_dict[i][2])
                print("Result:", result)
                print('Message: ' + str(count))
                print('MessageID (in case necessary):' + str(email_dict[i][3]))
                print('========================================\n')
                new_test[i] = email_dict[i]

                values = {'MessageID': str(email_dict[i][3]), 'Body': email_dict[i][2], 'Sender': email_dict[i][1], 'Subject': email_dict[i][0]}
                result_formatted.append(values)

            count += 1

        # ER.trash_message(service)
        response_obj = {
            "success": True,
            "data": {
                "emails": new_test
            }
        }
        return response_obj


# call the api to remove the email from spam folder
# noinspection PyUnresolvedReferences
@api.route("/spamfilter/untrash/<messid>")
class Untrash(Resource):

    @openid_required
    def post(self,messid):
        user_identifier = get_openid_identity()
        ER.untrash_message(user_identifier,messid)
        response_obj = {
            "success": True,
        }
        return response_obj

@app.route("/spamfilter/whitelist/")
class WhitelistApi(Resource):

    @openid_required
    def get(self):
        whitelisted_emails = []
        p_output = open('whitelist.txt', 'r')
        for element in p_output.readlines():
            whitelisted_emails.append(element.strip())
        p_output.close()
        response_obj = {
            "success": True,
            "data": whitelisted_emails
        }
        return response_obj

    @openid_required
    def post(self):
        em = input("Enter emails address not to be marked as spam: ")
        with open('whitelist.txt', "a") as output:
            output.write(em+'\n')
        response_obj = {
            "success": True
        }
        return response_obj
