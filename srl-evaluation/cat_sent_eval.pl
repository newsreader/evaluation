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
    open(my $IN,"<",$f);
    chomp(my @lines = <$IN>);
    close $IN;

    my $numSent = 0;
    my $emptyLine = 0;
    
    for (my $i=0; $i<@lines; $i++){
	my $line = $lines[$i];
    #while(<IN>){
	if($numSent < 6 && $numSent != 1){
	    if($line =~ m/^(\t)*$/){
		$numSent ++;
		$numLPrint ++;
		if($emptyLine == 1){
		    $emptyLine = 2;
		}
		else{
		    $emptyLine = 1;
		}
	    }
	    elsif ($gold){
		$emptyLine = 0;
		my @elts = split("\t",$line);
		if ($elts[13] ne "_" && $elts[13] =~ /_/){
		    my $lemmaPred = $elts[2];
		    my @token = split("_",$elts[13]);
		    for (my $j=$i+1; $j<$i+@token; $j++){
			my @eltsTemp = split("\t",$lines[$j]);
			$lemmaPred .= "_".$eltsTemp[2];
		    }
		    $lemmaPred .= ".01";
		    $line =~ s/\t$elts[13]\t/\t$lemmaPred\t/;
		}
		elsif ($elts[13] ne "_"){
		    my $lemmaPred = $elts[2].".01";
		    $line =~ s/\t$elts[13]\t/\t$lemmaPred\t/;
		}
	    }
	    else{
		$emptyLine = 0;
		my @elts = split("\t",$line);
		if ($elts[13] ne "_" && ($elts[13] =~ /\.0[^1]/ || $elts[13] =~ /\.1\d/)){
		    my $lemmaPred = $elts[2].".01";
		    #$lemmaPred =~ s/\.(.*)$//;
		    $line =~ s/\t$elts[13]\t/\t$lemmaPred\t/;
		}
		$line =~ s/\tAM-([^\t]+)/\tAm-$1/g;
		$line =~ s/\tam-((ext)|(mnr)|(neg)|(tmp)|(adv)|(cau)|(dir)|(dis)|(mod)|(pnc)|(tmp))/\tAm-OTHER/gi;
		$line =~ s/\tc-a1/\tA1/gi;
		$line =~ s/\tr-((a0)|(a1)|(a2)|(am-loc)|(am-tmp))/\t$1/gi;
	    }
	    #$numLPrint ++;
	    if($emptyLine == 0 || $emptyLine == 1){
		print OUT $line."\n";
	    }
	}
	elsif($numSent == 1){
	    if($line =~ m/^(\t)*$/){
		$numSent ++;
		#$numLPrint ++;
	    }
	}
	else{
	    last;
	}
    }
    #close IN;
}

close OUT;

print $numLPrint."\n";
