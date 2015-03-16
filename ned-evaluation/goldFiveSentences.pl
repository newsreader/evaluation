#!/usr/bin/perl -w

use XML::LibXML;

use strict;
use locale;

my $gold = $ARGV[0];
my $out = $ARGV[1];

my $parser = XML::LibXML->new();

opendir(my $dh, $gold) || die "can't opendir $gold: $!";
my @docs = readdir($dh);
closedir $dh;

open(O,">$out") or die "can't open $out file\n";
foreach my $d (@docs){
    if ($d =~ /\.naf$/){
	my $doc    = $parser->parse_file("$gold/$d");    
	my @wfs = $doc->findnodes("/NAF/text/wf");
	my $sent = 0;
	my $pos = 0;
	my $max = 0;
	while ($pos < $#wfs && $sent <= 6){
	    my $wf = $wfs[$pos];
	    $sent = $wf->getAttribute("sent");
	    if ($sent <= 6){
		$max = $wf->getAttribute("id");
	    }	    
	    $pos++;
	}
	
	foreach my $entity ($doc->findnodes("/NAF/entities/entity")){
	    my $span;
	    my @targets = $entity->findnodes("references/span/target");
	    my $pos = 0;
	    if ($targets[0]->getAttribute("id") <= $max){
		while ($pos < $#targets){
		    my $id = $targets[$pos]->getAttribute("id");
		    $span .= $id . "-";
		    $pos++;
		}
		$span .= $targets[$#targets]->getAttribute("id");
		
		my @refs = $entity->findnodes("externalReferences/externalRef");
		if ($#refs >= 0){
		    my $ref = $refs[0]->getAttribute("reference");
		    if ($ref =~ /dbpedia/){
			$ref =~ /.*\/(.*?)$/;
			$ref = $1;
			print O "$d\t$span\t$ref\n";
		    }
		}
	    }
	}
    }
}
close(O);
