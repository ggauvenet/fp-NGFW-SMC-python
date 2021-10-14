import logging
import time
from smc import session
from smc.elements.servers import LogServer
from smc.api.exceptions import UpdateElementFailed
from smc.administration.system import AdminDomain
from smc.elements.user import AdminUser
from smc_info import *


logging.getLogger()
logging.basicConfig(level=logging.INFO)

error_update = "Element reference breaks domain boundary restriction"
domain_name = "domain_test"
admin_name = "admin_test"
admin_password = "MySuperPassword2021!"

if __name__ == "__main__":

    session.login(url=SMC_URL, api_key=API_KEY, verify=False, timeout=120,
                  api_version=API_VERSION)

    # Create SMC Domain
    if AdminDomain.objects.filter(domain_name, exact_match=True):
        AdminDomain(domain_name).delete()
        logging.info("Domain [%s] has been deleted", domain_name)
    AdminDomain.create(name=domain_name)

    # Create new SMC Admin
    if AdminUser.objects.filter(name=admin_name):
        AdminUser(admin_name).enable_disable()
        time.sleep(1)
        AdminUser(admin_name).delete()

    admin = AdminUser.create(admin_name, superuser=True)
    admin.change_password(admin_password)

    session.logout()

    session.login(url=SMC_URL, api_version='6.8', login=admin_name, pwd=admin_password,
                  domain=domain_name)

    try:
        LogServer("Log Server").update(comment='updated in sub domain')
    except UpdateElementFailed as error:
        logging.info("Update of log server failed but is is expected")
        assert str(error).__contains__(error_update), \
            logging.error("Expecting to have [%s] but got [%s]", error_update, error)

    session.logout()

    # Cleanup env
    session.login(url=SMC_URL, api_key=API_KEY, verify=False, timeout=120,
                  api_version=API_VERSION)

    # Create SMC Domain
    AdminDomain(domain_name).delete()
    logging.info("Domain [%s] has been deleted", domain_name)

    # Create new SMC Admin
    AdminUser(admin_name).enable_disable()
    time.sleep(1)
    AdminUser(admin_name).delete()

    session.logout()