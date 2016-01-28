#Author: Anne-Lyse Minard
#Date: July 2015
#Version: 1.1

#synopsis: perl evaluation_factuality_v3.0.pl gold_folder/ sys_folder/ 

use strict;
use warnings;

my @files_gold = glob($ARGV[0]."*");
my @files_sys = glob($ARGV[1]."*");

my ($tp, $fp, $fn) = (0,0,0);

my %classes;
my %classes_fp;
my %classes_fn;
my %classes_fc;

my $col_event = 2;
my $col_pol = 3;
my $col_cert = 4;
my $col_time = 5;

my %att_tp = ();
my %att_fn = ();
my %att_fp = ();
my %att_fc = ();

my $nb_ev = 0;

my $all_att = 0;
my $all_att_false = 0;

my $no_att_fp = 0;
my $no_att_fn = 0;
my $no_att_tp = 0;

my $strict_match = 0;

my %listFilesSysId = ();
for my $fileS (@files_sys){
    my ($numDoc) = ($fileS =~ /$ARGV[1](\d+)[\-\_]/);
    $listFilesSysId{$numDoc} = $fileS;
}

for my $fileG (@files_gold){
    my @references;
    
    open(IN,'<'.$fileG);
    while(<IN>){
	if(/\t/){
	    s/\n$//;
	    my @elts = split("\t",$_);
	    push(@references, \@elts);
	}
	#my @temp = [];
	#push(@lines, @temp);
    }
    close IN;

    my ($numDoc) = ($fileG =~ /$ARGV[0](\d+)[\-\_]/);
    
    my @predictions;

    if (exists($listFilesSysId{$numDoc})){
	my $fileS = $listFilesSysId{$numDoc};
	open(IN,'<'.$fileS);
	while(<IN>){
	    if(/\t/){
		s/\n$//;
		my @elts = split("\t",$_);
		push(@predictions, \@elts);
	    }
	    #my @temp = [];
	    #push(@lines, @temp);
	}
	close IN;
    }
    else{
	die $numDoc." doesn't exist in the folder ".$ARGV[1]."\n";
    }
    
    for (my $i=0; $i<@references; $i++){
	my $temp = $references[$i];
	my @refelts = @$temp;
	$temp = $predictions[$i];
	my @syselts = @$temp;

	if(@refelts > 2){

	    #gold: B-EVENT or I-EVENT with fact annotated, sys: B-EVENT or I-EVENT
	    if ((($refelts[$col_event] eq "B-EVENT" && $syselts[$col_event] =~ /EVENT/) || ($syselts[$col_event] eq "B-EVENT" && $refelts[$col_event] =~ /EVENT/)) && ($refelts[$col_pol] ne "O" || $refelts[$col_cert] ne "O" || $refelts[$col_time] ne "O")){
		
		my $match = 0;
		if($strict_match && $refelts[$col_event] eq "B-EVENT" && $syselts[$col_event] eq "B-EVENT"){
		    if($i+1 < @references){
			if ($references[$i+1] !~ /I-EVENT/ && $predictions[$i+1] !~ /I-EVENT/){
			    $match = 1;
			}
			else{
			    my $endEv = 0;
			    my $j = $i+1;
			    while (!$endEv && $j<@references){
				if($references[$j] !~ /I-EVENT/ || $predictions[$j] !~ /I-EVENT/){
				    if($references[$j] !~ /I-EVENT/ && $predictions[$j] !~ /I-EVENT/){
					$match = 1;
				    }
				    $endEv = 1;
				}
				$j++;
			    }
			}
		    }
		    else{
			$match = 1;
		    }
		}

		if($match || !$strict_match){
		
		    $nb_ev += 1;
		    
		    #polarity
		    if ($refelts[$col_pol] eq $syselts[$col_pol]){
			$att_tp{"pol"} += 1;
			if (not(exists($classes{"POL_".$refelts[$col_pol]}))){
			    $classes{"POL_".$refelts[$col_pol]} = 0;
			}
			$classes{"POL_".$refelts[$col_pol]} += 1;
		    }
		    elsif ($refelts[$col_pol] eq "O"){
			$att_fp{"pol"} += 1;
		    }
		    elsif ($refelts[$col_pol] ne $syselts[$col_pol]){
			$att_fc{"pol"} += 1;
			if (not(exists($classes_fc{"POL_".$refelts[$col_pol]}))){
			    $classes_fc{"POL_".$refelts[$col_pol]} = 0;
			}
			$classes_fc{"POL_".$refelts[$col_pol]} += 1;
			
			#FP
			if (not(exists($classes_fp{"POL_".$syselts[$col_pol]}))){
			    $classes_fp{"POL_".$syselts[$col_pol]} = 0;
			}
			$classes_fp{"POL_".$syselts[$col_pol]} += 1;
			#FN
			if (not(exists($classes_fn{"POL_".$refelts[$col_pol]}))){
			    $classes_fn{"POL_".$refelts[$col_pol]} = 0;
			}
			$classes_fn{"POL_".$refelts[$col_pol]} += 1;
		    }
		    #elsif ($syselts[$col_pol] eq "O"){
			#$att_fn{"pol"} += 1;
		    #}

		    #certainty
		    if ($refelts[$col_cert] eq $syselts[$col_cert]){
			$att_tp{"cert"} += 1;
			if (not(exists($classes{"CERT_".$refelts[$col_cert]}))){
			    $classes{"CERT_".$refelts[$col_cert]} = 0;
			}
			$classes{"CERT_".$refelts[$col_cert]} += 1;
		    }
		    elsif ($refelts[$col_cert] eq "O"){
			$att_fp{"cert"} += 1;
		    }
		    elsif ($refelts[$col_cert] ne $syselts[$col_cert]){
			$att_fc{"cert"} += 1;
			if (not(exists($classes_fc{"CERT_".$refelts[$col_cert]}))){
			    $classes_fc{"CERT_".$refelts[$col_cert]} = 0;
			}
			$classes_fc{"CERT_".$refelts[$col_cert]} += 1;

			#FP
			if (not(exists($classes_fp{"CERT_".$syselts[$col_cert]}))){
			    $classes_fp{"CERT_".$syselts[$col_cert]} = 0;
			}
			$classes_fp{"CERT_".$syselts[$col_cert]} += 1;
			#FN
			if (not(exists($classes_fn{"CERT_".$refelts[$col_cert]}))){
			    $classes_fn{"CERT_".$refelts[$col_cert]} = 0;
			}
			$classes_fn{"CERT_".$refelts[$col_cert]} += 1;
		    }
		    #elsif ($syselts[$col_cert] eq "O"){
			#$att_fn{"cert"} += 1;
		    #}

		    #time
		    if ($refelts[$col_time] eq $syselts[$col_time]){
			$att_tp{"time"} += 1;
			if (not(exists($classes{"TIME_".$refelts[$col_time]}))){
			    $classes{"TIME_".$refelts[$col_time]} = 0;
			}
			$classes{"TIME_".$refelts[$col_time]} += 1;
		    }
		    elsif ($refelts[$col_time] eq "O"){
			$att_fp{"time"} += 1;
		    }
		    elsif ($refelts[$col_time] ne $syselts[$col_time]){
			$att_fc{"time"} += 1;
			if (not(exists($classes_fc{"TIME_".$refelts[$col_time]}))){
			    $classes_fc{"TIME_".$refelts[$col_time]} = 0;
			}
			$classes_fc{"TIME_".$refelts[$col_time]} += 1;

			#FP
			if (not(exists($classes_fp{"TIME_".$syselts[$col_time]}))){
			    $classes_fp{"TIME_".$syselts[$col_time]} = 0;
			}
			$classes_fp{"TIME_".$syselts[$col_time]} += 1;

			#FN
			if (not(exists($classes_fn{"TIME_".$refelts[$col_time]}))){
			    $classes_fn{"TIME_".$refelts[$col_time]} = 0;
			}
			$classes_fn{"TIME_".$refelts[$col_time]} += 1;
		    }
		    #elsif ($syselts[$col_time] eq "O"){
			#$att_fn{"time"} += 1;
		    #}

		    #3 attributes right
		    if ($refelts[$col_pol] eq $syselts[$col_pol] && $refelts[$col_cert] eq $syselts[$col_cert] && $refelts[$col_time] eq $syselts[$col_time] ){
			$all_att += 1;
		    }
		    #3 attributes wrong
		    if ($refelts[$col_pol] ne $syselts[$col_pol] && $refelts[$col_cert] ne $syselts[$col_cert] && $refelts[$col_time] ne $syselts[$col_time] ){
			$all_att_false += 1;
		    }

		}

	    }
	    elsif ((($refelts[$col_event] =~ /EVENT/ && $syselts[$col_event] eq "B-EVENT") || ($syselts[$col_event] =~ /EVENT/ && $refelts[$col_event] eq "B-EVENT")) && $refelts[$col_pol] eq "O" && $refelts[$col_cert] eq "O" && $refelts[$col_time] eq "O"){
		$no_att_fn += 1;
	    }
	    elsif ($refelts[$col_event] eq "B-EVENT" && $syselts[$col_event] eq "O" && $refelts[$col_pol] eq "O" && $refelts[$col_cert] eq "O" && $refelts[$col_time] eq "O"){
		$no_att_tp += 1;
	    }
	    elsif ($refelts[$col_event] eq "B-EVENT" && $syselts[$col_event] eq "O" && $refelts[$col_pol] ne "O" && $refelts[$col_cert] ne "O" && $refelts[$col_time] ne "O"){
		$no_att_fp += 1;
	    }
	}
    }
}


print "nb events with 3 attributes correct: ".$all_att."\n";

my $recall_fact = $all_att/$nb_ev;
print "factuality (3 att), recall: ".$recall_fact."\n";

#Accuracy
my $recall_pol = $att_tp{"pol"}/$nb_ev;
my $recall_cert = $att_tp{"cert"}/$nb_ev;
my $recall_time = $att_tp{"time"}/$nb_ev;

print "polarity, accuracy (".$att_tp{"pol"}."/".$nb_ev."): ".$recall_pol."\n";
print "certainty, accuracy (".$att_tp{"cert"}."/".$nb_ev."): ".$recall_cert."\n";
print "time, accuracy (".$att_tp{"time"}."/".$nb_ev."): ".$recall_time."\n";

print "\n\t recall \t precision \t f1\n";

#R/P/F1 for each value
for my $cl (keys(%classes)){
    if(not(exists($classes_fn{$cl}))){
	$classes_fn{$cl} = 0;
    }
    if(not(exists($classes_fp{$cl}))){
	$classes_fp{$cl} = 0;
    }

    my $recall = $classes{$cl}/($classes{$cl}+$classes_fn{$cl});
    my $precision = $classes{$cl}/($classes{$cl}+$classes_fp{$cl});
    my $f1 = (2*$recall*$precision)/($recall+$precision);
    
    print $cl.": \t".$recall."\t".$precision."\t".$f1."\n";
}
