[![Build Status](https://travis-ci.org/oasis-roles/rhv_he_deploy.svg?branch=master)](https://travis-ci.org/oasis-roles/rhv_he_deploy)

rhv_he_deploy
=============

This role performs an installation of Red Hat Virtualization 4 in
self-hosted mode to a single host, using a templated answerfile to
ensure noninteractive installation. If installation to multiple hosts
is desired, each host must be configured as an independent RHV installation,
and the role must be run multiple times for each host.

Requirements
------------

Ansible 2.4 or higher

Red Hat Enterprise Linux 7 or equivalent

Valid Red Hat Subscriptions, including entitlements for Red Hat Virtualization

Terms
-----

Since this role installs a VM onto the host being configured, and vars for this
role can affect both the host being configured and the VM being configured on
that host. To clarify when a var will affect either the host or the instance,
the following terms are used throughout this role:

- `RHV`: Red Hat Virtualization
- `RHV host`: The host on which `hosted-engine` will run, and subsequently the
  first host that will be added to this RHV deployment.
- `RHVM`: Red Hat Virtualization Manager, also referred to in this document as
  `RHVM instance`.
- `oVirt`: RHV upstream project name, for our purposes effectively synonymous
  with "RHV"

Role Variables
--------------

Many variables in this role have the prefix `he_`, instead of the normal
and expected OASIS variable prefix of the role name. This is done to conform,
where possible, with an oVirt role currently in development that is expected
to supersede `hosted-engine` deployments at a later date. This variation in
variable naming is done in an attempt to be forward-compatible with that role.

[ovirt-ansible-hosted-engine-setup](https://github.com/oVirt/ovirt-ansible-hosted-engine-setup)

Where variable in this role are not used in the oVirt role, the expected
`rhv_he_deploy_` prefix is used.

### Required

The following variables are required for this role to function, and are
described in more detail below:

- `he_appliance_password`
- `he_admin_password`
- `he_fqdn`
- `he_vm_ip_addr`
- `he_vm_ip_prefix`
- `he_domain_type`
- `he_storage_domain_addr`
- `he_root_ssh_pubkey`


### Passwords

The RHVM instance root password, as well as the admin password for accessing
the RHV cluster management dashboard, are set using the answerfile.

This is potentially insecure, as the answerfile is sent to the RHV host
during the hosted-engine installation, and these password will be present
in the answerfile for the duration of the installation.

- `he_appliance_password`: root password for the RHVM instance
- `he_admin_password`: password for the "admin@internal" RHVM user

### Packages

- `rhv_he_deploy_rpms`: RPMs required for the hosted-engine install,
  defaults to `['ovirt-hosted-engine-setup']`

### Networking

The `hosted-engine` deployment requires a preallocated IP address in the same
subnet as the network that the RHV host will be using for RHV. Additionally,
a fully-qualified domain name (FQDN) for that IP address must be set up in
DNS to resolve to that address (forward and reverse). This is a pre-requisite
to running the playbook, and cannot be done by the playbook.

- `he_fqdn`: The FQDN of the RHVM instance created by hosted engine. This
  cannot be e.g. `localhost`, `localhost.localdomain`, etc. It must be a
  "real" and routable FQDN.
- `he_vm_ip_addr`: The IP address given to the RHVM instance
- `he_vm_ip_prefix`: The CIDR netmask of the subnet in which `he_vm_ip_addr`
  resides. Again, this must match the RHV host subnet.
- `he_bridge_if`: Optional, used to specify the interface that should be
  added to the oVirt management bridge when multiple interfaces are configured
  and hosted-engine cannot easily guess which interface to use.
- `he_mgmt_network`: Optional, name of bridge to configure, to which
  `he_bridge_if` will be attached. Defaults to `ovirtmgmt`.
- `he_vm_mac_addr`: Optional, used if a specific MAC address is required for
  the NIC created for the RHVM instance. Will be randomly generated if unset.
- `he_gateway`: Optional, will be the gateway given to the RHVM instance.
  hosted-engine will use the RHV host gateway by default.
- `he_dns_addr`: Optional comma-delimited list of nameserver that the RHVM
  instance will be configured to use. Will use the RHV host nameservers by
  default.
- `rhv_he_deploy_firewall_manager`: Optional firewall manage to use, can be
  one of `firewalld`, `iptables`, or null (null for no firewall management).
  Defaults to `firewalld`.

### RHVM instance

In addition to the networking settings above, hosted-engine exposes several
options for configuring the RHVM instance during its creation.

- `he_root_ssh_pubkey`: SSH public key to install into the root user's
  `authorized_keys` file in the RHVM instance. Value is a string, not a file
  name.
- `he_vcpus`: The number of VCPUs for the RHVM instance
- `he_mem_size_MB`: The amount of memory for the RHVM instance, in megabytes
- `he_disk_size_GB`: The size of the RHVM instance's disk
- `he_time_zone`: Optional timezone for the RHVM instance, default "UTC"
- `he_emulated_machine`: Optional, the machine type to emulate (i.e. the
  `--machine` argument to `virt-install`.

### Storage

The vars used to generate the storage configuration sections of the answerfile
vary greatly depending on which storage domain type is being configured. These
vars are specific to the initial `data` storage domain created during the
hosted-engine deployment.

- `he_domain_type`: One of `nfs`, `glusterfs`, or `iscsi`. Additionally, the
  values `nfs3`, `nfs4`, and `fc` are available but not supported.
- `he_storage_domain_addr`: Address or host name of the host providing storage.
- `he_storage_domain_path`: Path to exported storage on the storage host, used
  by `nfs` and `glusterfs`.
- `he_storage_domain_name`: Human-readable name given to the storage domain
  created in RHVM. Defaults to `hosted_storage`.
- `he_storage_datacenter_name`: Human-readable name given to the datacenter
  created in RHVM. Defaults to `hosted_datacenter`.
- `he_mount_options`: Mount options used to mount the storage domain on the
  RHV host. Can be left undefined if no special mount options are needed.

#### NFS

- `he_nfs_version`: Optional, one of `auto`, `v3`, `v4`, `v4_1`, and `v4_2`.
  Defaults to `auto`.

#### iSCSI

- `he_iscsi_tpgt`: iSCSI Portal
- `he_iscsi_portal_addr`: iSCSI Portal Address
- `he_iscsi_portal_port`: iSCSI Portal Port
- `he_iscsi_username`: iSCSI Username
- `he_iscsi_target`: iSCSI Password
- `he_lun_id`: SCSI LUN ID

Any unspecified iSCSI values default to "None".

### SMTP Notification

By default, email notifications are sent from `root@localhost` on the
RHV host being configured, and delivered to `root@localhost` on that
same host.

- `he_smtp_server`: Server to which to send notification emails.
  Defaults to `localhost`.
- `he_smtp_port`: Port to use for relaying mail. Defaults to `25`.
- `he_source_email`: "From" address in sent mail. Defaults to `root@localhost`.
- `he_dest_email`: "To" address in sent mail. Defaults to `root@localhost`.

### Logging

If desired, logs from the hosted-engine installation can be retrieved and
stored locally using the following vars:

- `rhv_he_deploy_collect_logs`: If `true`, collect logs to ansible controller.
  Defaults to `false`.
- `rhv_he_deploy_log_dir`: Directory on the ansible controller in which to
  collect logs. Defaults to `{{ playbook_dir }}/rhv_he_deploy_logs`.

The collected logs will included all logs generated by `hosted-engine` itself,
as well as `stdout` and `stderr` from the `hosted-engine` deployment. The fqdn
of the host from which logs are being collected will be included in the log
path, and logs will only be collected if a `hosted-engine` deployment runs.

### Privilege Escalation

- `rhv_he_deploy_become`: Enables privilege escalation if true. Defaults to
  `true`
- `rhv_he_deploy_become_user`: User to become when privilege escalation is
  enabled. Defaults to `root`

Dependencies
------------

None

Example Playbook
----------------

All roles used in this example are installable via Ansible Galaxy.

```yaml
# Ensure that only a single host is in this host group
- hosts: rhv_he_deploy_host
  vars:
    # RHSM Vars
    rhsm_username: your_username
    rhsm_password: your_password
    rhsm_pool_ids:
      - your_pool_ids
    rhsm_repositories:
      enabled:
        - rhel-7-server-rpms
        - rhel-7-server-rhv-4-mgmt-agent-rpms
        - rhel-7-server-ansible-2-rpms
    # RHV HE deploy vars, documented above
    he_appliance_password: notsecret
    he_admin_password: notsecret
    he_fqdn: your.fqdn.domain
    he_vm_ip_addr: 1.2.3.4
    he_vm_ip_prefix: 24
    he_root_ssh_pubkey: "{{ lookup('file', '/path/to/id_rsa.pub') }}"
    he_domain_type: glusterfs
    he_storage_domain_addr: existing-storage-domain-host.domain
    he_storage_domain_path: /path/to/data
  roles:
    # subscribed system is required
    - oasis-roles.rhsm
    # services recommended by RHV install docs
    - oasis-roles.firewalld
    - oasis-roles.chrony
    - oasis-roles.cockpit
    # the actual deployment
    - oasis-roles.rhv_he_deploy
```

License
-------

GPLv3

Author Information
------------------

Sean Myers <sean.myers@redhat.com>
