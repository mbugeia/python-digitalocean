# -*- coding: utf-8 -*-
import requests
from .Action import Action
from .Image import Image
from .Kernel import Kernel
from .baseapi import BaseAPI
from .SSHKey import SSHKey

class Droplet(BaseAPI):
    def __init__(self, *args, **kwargs):
        # Defining default values
        self.id = None
        self.name = None
        self.memory = None
        self.vcpus = None
        self.disk = None
        self.region = []
        self.status = None
        self.image = None
        self.size = None
        self.locked = None
        self.created_at = None
        self.status = None
        self.networks = []
        self.kernel = None
        self.backup_ids = []
        self.snapshot_ids = []
        self.action_ids = []
        self.features = []
        self.ip_address = None
        self.private_ip_address = None
        self.ip_v6_address = None
        self.ssh_keys = None
        self.backups = None
        self.ipv6 = None
        self.private_networking = None
        self.user_data = None

        # This will load also the values passed
        super(Droplet, self).__init__(*args, **kwargs)

    @classmethod
    def get_object(cls, api_token, droplet_id):
        """
            Class method that will return a Droplet object by ID.
        """
        droplet = cls(token=api_token, id=droplet_id)
        droplet.load()
        return droplet

    def __check_actions_in_data(self, data):
        # reloading actions if actions is provided.
        if data.has_key(u"actions"):
            self.action_ids = []
            for action in data[u'actions']:
                self.action_ids.append(action[u'id'])

    def get_data(self, *args, **kwargs):
        """
            Customized version of get_data to perform __check_actions_in_data
        """
        data = super(Droplet, self).get_data(*args, **kwargs)
        if kwargs.has_key("type"):
            if kwargs["type"] == "POST":
                self.__check_actions_in_data(data)
        return data

    def load(self):
        droplets = self.get_data("droplets/%s" % self.id)
        droplet = droplets['droplet']

        for attr in droplet.keys():
            setattr(self,attr,droplet[attr])

        for net in self.networks['v4']:
            if net['type'] == 'private':
                self.private_ip_address = net['ip_address']
            if net['type'] == 'public':
                self.ip_address = net['ip_address']
        if self.networks['v6']:
            self.ip_v6_address = droplet.networks['v6'][0]['ip_address']
        return self

    def power_on(self):
        """
            Boot up the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'power_on'}
        )

    def shutdown(self):
        """
            shutdown the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'shutdown'}
        )

    def reboot(self):
        """
            restart the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'reboot'}
        )

    def power_cycle(self):
        """
            restart the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'power_cycle'}
        )

    def power_off(self):
        """
            restart the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'power_off'}
        )

    def reset_root_password(self):
        """
            reset the root password
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'password_reset'}
        )

    def resize(self, new_size):
        """
            resize the droplet to a new size
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={"type": "resize", "size": new_size}
        )

    def take_snapshot(self, snapshot_name):
        """
            Take a snapshot!
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={"type": "snapshot", "name": snapshot_name}
        )

    def restore(self, image_id):
        """
            Restore the droplet to an image ( snapshot or backup )
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={"type":"restore", "image": image_id}
        )

    def rebuild(self, image_id=None):
        """
            Restore the droplet to an image ( snapshot or backup )
        """
        if self.image_id and not image_id:
            image_id = self.image_id

        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={"type": "rebuild", "image": image_id}
        )

    def enable_backups(self):
        """
            Enable automatic backups (Not yet implemented in APIv2)
        """
        print("Not yet implemented in APIv2")

    def disable_backups(self):
        """
            Disable automatic backups
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'disable_backups'}
        )

    def destroy(self):
        """
            Destroy the droplet
        """
        return self.get_data(
            "droplets/%s" % self.id,
            type="DELETE"
        )

    def rename(self, name):
        """
            Rename the droplet
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'rename', 'name': name}
        )

    def enable_private_networking(self):
        """
           Enable private networking on an existing Droplet where available.
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'enable_private_networking'}
        )

    def enable_ipv6(self):
        """
            Enable IPv6 on an existing Droplet where available.
        """
        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type': 'enable_ipv6'}
        )

    def change_kernel(self, kernel):
        """
            Change the kernel to a new one
        """
        if type(kernel) != Kernel:
            raise Exception("Use Kernel object")

        return self.get_data(
            "droplets/%s/actions/" % self.id,
            type="POST",
            params={'type' : 'change_kernel', 'kernel': kernel.id}
        )

    def __get_ssh_keys_id(self):
        """
            Check and return a list of SSH key IDs according to DigitalOcean's
            API. This method is usde to check and create a droplet with the
            correct SSH keys.
        """
        ssh_keys_id = list()
        for ssh_key in self.ssh_keys:
            if type(ssh_key) in [int, long]:
                ssh_keys_id.append( int(ssh_key) )

            elif type(ssh_key) == SSHKey:
                ssh_keys_id.append(ssh_key.id)

            elif type(ssh_key) in [str, unicode]:
                key = SSHKey()
                key.token = self.token
                results = key.load_by_pub_key(ssh_key)

                if results == None:
                    key.public_key = ssh_key
                    key.name = "SSH Key %s" % self.name
                    key.create()
                else:
                    key = results

                ssh_keys_id.append(key.id)
            else:
                raise Exception("Droplet.ssh_keys should be a list of IDs or public keys")

        return ssh_keys_id

    def create(self, *args, **kwargs):
        """
            Create the droplet with object properties.

            Note: Every argument and parameter given to this method will be
            assigned to the object.
        """
        for attr in kwargs.keys():
            setattr(self,attr,kwargs[attr])

        data = {
                "name": self.name,
                "size": self.size,
                "image": self.image,
                "region": self.region,
                "ssh_keys[]": self.__get_ssh_keys_id(),
            }

        if self.backups:
            data['backups'] = True

        if self.ipv6:
            data['ipv6'] = True

        if self.private_networking:
            data['private_networking'] = True

        if self.user_data:
            data["user_data"] = self.user_data

        data = self.get_data(
            "droplets",
            type="POST",
            params=data
        )

        if data:
            self.id = data['droplet']['id']

        if data[u'droplet'].has_key(u"action_ids"):
            self.action_ids = []
            for id in data[u'droplet'][u'action_ids']:
                self.action_ids.append(id)

    def get_events(self):
        """
            A helper function for backwards compatability.
            Calls get_actions()
        """
        return self.get_actions()

    def get_actions(self):
        """
            Returns a list of Action objects
            This actions can be used to check the droplet's status
        """
        answer = self.get_data(
            "droplets/%s/actions" % self.id,
            type="GET"
        )

        actions = []
        for action_dict in answer['actions']:
            action = Action(**action_dict)
            action.token = self.token
            action.droplet_id = self.id
            action.load()
            actions.append(action)
        return actions

    def get_action(self, action_id):
        """
            Returns a specific Action by its ID.
        """
        return Action.get_object(
            api_token=self.token,
            action_id=action_id
        )

    def get_snapshots(self):
        """
            This method will return the snapshots/images connected to that
            specific droplet.
        """
        snapshots = list()
        for id in self.snapshot_ids:
            snapshot = Image()
            snapshot.id = id
            snapshot.token = self.token
            snapshots.append(snapshot)
        return snapshots

    def get_kernel_available(self):
        """
            Get a list of kernels available
        """

        kernels = list()
        data = self.get_data("droplets/%s/kernels/" % self.id)
        while True:
                for jsond in data[u'kernels']:
                    kernel = Kernel(**jsond)
                    kernel.token = self.token
                    kernels.append(kernel)
                url = data[u'links'][u'pages'].get(u'next')
                if not url:
                        break
                data = self.get_data(data[u'links'][u'pages'].get(u'next'))

        return kernels

    def __str__(self):
        return "%s %s" % (self.id, self.name)
