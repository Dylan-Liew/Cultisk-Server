from flask_restx import Namespace, Resource

import cultisk.Email_Retrieve as ER
from cultisk import app
from cultisk.Models import MainFilter
from cultisk.helper import openid_required, get_openid_identity

api = Namespace("spam-filter", description="Email Filter")


@api.route("/spamfilter/")
class MainFilter(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        # service=ER.return_sevice(user_identifier)
        test = ER.getEmails(user_identifier)
        count = 1
        new_test = {}
        for i in test:
            result = MainFilter.filter(message=test[i][2])
            # print("MessageID: " + str(i))
            if result == 'spam':
                ER.trash_message(user_identifier, i)
                print("Subject:", test[i][0])
                print("Sender:", test[i][1])
                print("Body:", test[i][2])
                print("Result:", result)
                print('Message: ' + str(count))
                print('========================================\n')
                new_test[i] = test[i]
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


# noinspection PyUnresolvedReferences
@app.route("/spamfilter/<messid>/")
class EmailDetail(Resource):

    @openid_required
    def post(self,messid):
        user_identifier = get_openid_identity()
        mail = ER.get_one_email(user_identifier,messid)
        mail1 = mail[messid]
        print("Body:" + str(mail1[2]))
        body = mail1[2]
        response_obj = {
            "success": True,
            "data": body
        }
        return response_obj


@app.route("/spamfilter/whitelist/")
class whitelist(Resource):

    @openid_required
    def get(self):
        s_list = []
        p_output = open('Whitelist.txt', 'r')
        for element in p_output.readlines():
            s_list.append(element.strip())
        p_output.close()
        response_obj = {
            "success": True,
            "data": s_list
        }
        return response_obj

    @openid_required
    def post(self):
        em = input("Enter emails address not to be marked as spam: ")
        with open('Whitelist.txt', "a") as output:
            output.write(em+'\n')
        response_obj = {
            "success": True
        }
        return response_obj
