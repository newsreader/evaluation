#perl cat_sent_eval.pl folder_name output_file
#concatene the 6 first sentences of all the files of a corpus

#if the corpus given in input is the system output corpus, then some modifications on the labels are done.

use strict;
use warnings;

my @files = glob($ARGV[0]."*.conll");

my $gold = 1;

open(OUT, ">".$ARGV[1]);

if ($ARGV[1] =~ /sys/){
    $gold = 0;
}

my $numLPrint=0;
foreach my $f (@files){
    open(IN,"<".$f);
    my $numSent = 0;
    while(<IN>){
	if($numSent < 6 && $numSent != 1){
	    if(m/^(\t)*$/){
		$numSent ++;
		$numLPrint ++;
	    }
	    elsif ($gold){
		my @elts = split("\t",$_);
		if ($elts[13] ne "_"){
		    my $lemmaPred = $elts[2].".01";
		    s/\t$elts[13]\t/\t$lemmaPred\t/;
		}
	    }
	    else{
		my @elts = split("\t",$_);
		if ($elts[13] ne "_" && ($elts[13] =~ /\.0[^1]/ || $elts[13] =~ /\.1\d/)){
		    my $lemmaPred = $elts[2].".01";
		    #$lemmaPred =~ s/\.(.*)$//;
		    s/\t$elts[13]\t/\t$lemmaPred\t/;
		}
		s/\tAM-([^\t]+)/\tAm-$1/g;
		s/\tam-((ext)|(mnr)|(neg)|(tmp)|(adv)|(cau)|(dir)|(dis)|(mod)|(pnc)|(tmp))/\tAm-OTHER/gi;
		s/\tc-a1/\tA1/gi;
		s/\tr-((a0)|(a1)|(a2)|(am-loc)|(am-tmp))/\t$1/gi;
	    }
	    #$numLPrint ++;
	    print OUT $_;
	}
	elsif($numSent == 1){
	    if(m/^(\t)*$/){
		$numSent ++;
		#$numLPrint ++;
	    }
	}
	else{
	    last;
	}
    }
    close IN;
}

close OUT;

print $numLPrint."\n";
