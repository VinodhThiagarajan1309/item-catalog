# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", path: "pg_config.sh"
  config.vm.box = "hashicorp/precise32"
  # config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 9000, host: 9000
  config.vm.network "forwarded_port", guest: 10000, host: 10000
  config.vm.network "forwarded_port", guest: 11000, host: 11000
end
