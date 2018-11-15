import os

try:
    # py3
    from configparser import ConfigParser
except ImportError:
    # py2
    from ConfigParser import ConfigParser

answerfile = os.path.join(os.environ['MOLECULE_SCENARIO_DIRECTORY'],
                          'rhv_he_deploy/answerfile_none/answers.conf')

parsed = ConfigParser()
parsed.read(answerfile)

expected = {
    'OVEHOSTED_NETWORK': [
        'bridgeIf',
        'firewallManager',
        'gateway'
    ],
    'OVEHOSTED_STORAGE': [
        'iSCSIPortal',
        'iSCSIPortalIPAddress',
        'iSCSIPortalPort',
        'iSCSIPortalUser',
        'iSCSITargetName',
        'LunID'
    ],
    'OVEHOSTED_VM': [
        'cloudinitVMDNS',
        'emulatedMachine',
        'vmMACAddr'
    ]
}


def pytest_generate_tests(metafunc):
    # parametrize tests by key for independent assertions
    # against each value in the template using the str_or_none macro
    idlist = []
    argvalues = []
    for prefix, values in expected.items():
        for value in values:
            key = '/'.join((prefix, value))
            idlist.append(key)
            argvalues.append(key)
    metafunc.parametrize('key', argvalues, ids=idlist)


def test_answerfile_none(key):
    assert parsed.get('environment:default', key) == 'none:None'
