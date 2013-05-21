
# Tendenci Demo Appliance

Tendenci virtual machine images contain a fully functional tendenci web site. It allows you to easily set up a demo site on your local machine with Virtual Box. 

## Requirements

* Minumum RAM: 1024 MB
* Minumum file storage: 24 GB

## Download the latest Tendenci VM appliance:
[OVA File](https://s3.amazonaws.com/tendenci-virtual-appliances/tendenci_vm.ova)


## Steps to import ova file

1. Install  or upgrade VirtualBox 4 or later [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads).
2. Import .ova file: Click File -> Import Appliance -> Open appliance and select the downloaded Tendenci ova file. Then follow the instruction to complete the import. 
3. Make sure Network Adapter 1 is attached to Bridged Adapter: Settings -> Network -> Adapter 1 -> Bridged Adapter

Once the import is done, you can start your Tendenci VM and access the demo site. 

The system login:

	username: tvm
	password: tvm
	
The admin account for the demo web site:

	username: admin
	password: admin