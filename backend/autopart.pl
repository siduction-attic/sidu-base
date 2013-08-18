#! /usr/bin/perl
#
# Usage: autopart.pl "$CMD" "$ANSWER" "$DISKS" "$PARTS" "$BOOT" "$ROOT" "$HOME" "$SWAP"

use strict;

my $cmd = shift;
my $answer = shift;
my $diskInfo = shift;
my $partitions = shift;
my $boot = shift;
my $root = shift;
my $home = shift;
my $swap = shift;

my $s_fdisk = "/sbin/fdisk";
my $s_gdisk = "/sbin/gdisk";

my %s_wantedDiskType;
my %s_realDiskType;

# Builds all PV of a LVM
# @param physParts	a list of all PV partitions (which does not exist yet)
#                   e.g. "sda1-9-2048-1000000+sdb1-9-2048-1000000"
sub buildLVMs{
	my $physParts = shift;
	my @physParts = ;
	for $part (split(/\+/, $physParts)){
		my ($name, $no, $from, $to) = split(/-/, $part);
		buildLVM($name, $no, $from, $to, "mbr");
	}
}

# Builds one PV of a LVM
# @param name	name of the partition, e.g. sda1
# @param from	first record (of the disk)
# @param to		last record
sub buildLVM{
	my $partNo = shift;
	my $from = shift;
	my $to = shift;

}

# Finds the disk name for a given partition
# @param part	partition name, e.g. "sda1"
# @return       the disk name, e.g. "sda"
sub findDiskName{
	my $part = shift;
	my $rc;
	if ($part =~ /^([a-z]+)/){
		$rc = $1;
	}
	return $rc;
}

# Finds the partition table type.
# If the disk has no type (uninitialized) it will create a partition table
# @param part	e.g. "sda1"
# @return	"" (undef), "mbr" or "gpt"
sub findDiskType{
	my $part = shift;
	my $disk = findDiskName($part);
	
	my $rc;
	if ($s_realDiskType{$disk} ne ""){
		$rc = $s_realDiskType{$disk}; 
	} else {
		open(EXEC, "$s_gdisk -l /dev/$disk|") || die "gdisk: $!";
		while(<EXEC>){
			if (/MBR: present/){
				$rc = "mbr";
			} elsif (/GPT: present/){
				$rc = "gpt";
				last;
		}
		close EXEC;
		if ($rc eq ""){
			$partType = $s_wantedDiskType{$disk};
			if ($partType eq ""}{
				error("No partition table type given for $disk: mbr will be taken");
				$rc = "mbr";
		}
		$s_realDiskType{$disk} = $rc;
		createPartitionTable($disk, $rc);
	}
	return $rc;
}

# Creates a partition table for a disk.
# @param disk	disk name, e.g. sdc
# @param type	partition table type: "mbr" or "gpt"
sub createPartitionTable{
	my $disk = shift;
	my $type = shift;
	
	if ($type eq "mbr"){
		open(EXEC, "|$s_fdisk -l /dev/$disk");
		print EXEC "o\n", "w\n";
		close EXEC;
	} else {
		open(EXEC, "|$s_gdisk -l /dev/$disk");
		print EXEC "o\n", "w\n";
		close EXEC;
	}
}

# Handles an error message.
# @param msg	error message
sub error{
	my $msg = shift;
	print "+++ $msg\n";
}	
