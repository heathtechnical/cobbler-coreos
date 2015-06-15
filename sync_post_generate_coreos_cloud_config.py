import templar
import re
import os

def register():
    return "/var/lib/cobbler/triggers/sync/post/*"

def run(api,args,logger):

    input_template = open("/etc/cobbler/coreos-cloud-config.template")
    input_data = input_template.read()
    input_template.close()

    if not os.path.exists('/var/www/cobbler/coreos'):
        os.makedirs('/var/www/cobbler/coreos')

    for system in api.find_items('system'):
        metadata = { 'peers': None }
        if re.match('^coreos-', system.profile):
            logger.info("generating coreos cloud-config for %s" % system.name)
            metadata['interfaces'] = system.interfaces

            if "coreos-peers" in system.ks_meta:
                metadata['peers'] = system.ks_meta['coreos-peers']

            content = templar.Templar(api._config).render(input_data, metadata, None)

            f = open('/var/www/cobbler/coreos/cloud-config-' + system.name, 'w')
            f.write(content)
            f.close()

    return 0
