
debian_os = ['debian', 'ubuntu']
rhel_os = ['redhat', 'centos']


def test_distribution(host):
    assert host.system_info.distribution.lower() in debian_os + rhel_os


def test_repo_pinning_file(host):
    if host.system_info.distribution.lower() in debian_os:
        f = host.file('/etc/apt/preferences.d/dnsdist')
        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        f.contains('Package: dnsdist*')
        f.contains('Pin: origin repo.powerdns.com')
        f.contains('Pin-Priority: 600')


def test_package(host):
    p = host.package('dnsdist')
    assert p.is_installed


def test_configuration(host):
    f = host.file('/etc/dnsdist/dnsdist.conf')
    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_service(host):
    # Using Ansible to mitigate some issues with the service test on debian-8
    s = host.ansible('service', 'name=dnsdist state=started enabled=yes')

    assert s["changed"] is False


def systemd_override(host):
    smgr = host.ansible("setup")["ansible_facts"]["ansible_service_mgr"]
    if smgr == 'systemd':
        fname = '/etc/systemd/system/pdns.service.d/override.conf'
        f = host.file(fname)

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        assert 'LimitCORE=infinity' in f.content
