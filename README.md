# cobbler-coreos

Cobbler trigger to generate CoreOS cloud-config files.

Although Cobbler doesn't have native support for CoreOS, you can boot systems 
from the kernel/initrd directly:

    # cobbler distro add \
    --name coreos-alpha-709 \
    --kernel /tmp/coreos/coreos_production_pxe.vmlinuz \
    --initrd /tmp/coreos/coreos_production_pxe_image.cpio.gz
    
    # cobbler profile add \
    --name coreos-alpha-709 \
    --distro=coreos-alpha-709

    # cobbler system add \
    --name coreos01 \
    --profile coreos-alpha-709 \
    --netboot true \
    --hostname coreos01.local
    --static false \
    --interface eth0 \
    --dns-name coreos01.local \
    --ip-address 10.0.0.71 \
    --subnet 255.255.255.0 \
    --mac 00:00:00:00:00:00 \
    --gateway 10.0.0.1

Using this trigger, we can get cobbler to generate a per-system cloud-config 
for us, so checkout the repo and install the trigger and template file:

    # git clone https://github.com/heathtechnical/cobbler-coreos.git
    
    # cp cobbler-coreos/sync_post_generate_coreos_cloud_config.py /usr/lib/python2.6/site-packages/cobbler/modules
    
    # cp cobbler-coreos/coreos-cloud-config.template /etc/cobbler

Edit the template file as you see fit.

We need to then add some kernel options to the distro:

	# cobbler distro edit \
	--name coreos-alpha-709 \
	--kopts "coreos.autologin=tty1 cloud-config-url=http://@@server@@/cblr/coreos/cloud-config-@@system_name@@'

This will ensure when we boot our system they point at their own cloud-config 
files.

Restart cobblerd and sync:

    # service cobblerd restart
    # cobbler sync

You should now see per-system cloud-config files in /var/www/cobbler/coreos.

## Default configuration
The default template provides a somewhat static setup - we pass a list of peers 
to etcd and therefore don't need a discovery token and we define etcd 
interfaces statically too.

In order to provide this sort of setup the trigger looks for a kickstart metadata 
tag 'coreos-peers'.  This needs to be set to the list of systems in the cluster, 
for a three node setup, this would look like this:

    # cobbler system report --name coreos01 | grep Meta
	Kickstart Metadata             : {}
	
    # cobbler system report --name coreos02 | grep Meta
	Kickstart Metadata             : {'coreos-peers': '10.0.0.71:7001,10.0.0.72:7001,10.0.0.73:7001'}
	
    # cobbler system report --name coreos03 | grep Meta
	Kickstart Metadata             : {'coreos-peers': '10.0.0.71:7001,10.0.0.72:7001,10.0.0.73:7001'}

Note that the first system is our initial leader so we don't specify a peer list.
