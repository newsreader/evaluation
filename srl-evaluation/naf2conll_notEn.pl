use strict;
use XML::LibXML;

#
# Usage: perl naf2conll.pl input-naf-file output-conll-file [fullspan]
#


my $parser = XML::LibXML->new();
$parser->keep_blanks(0);
my $doc = $parser->parse_file($ARGV[0]);
my $naf_root = $doc->documentElement();

my $words;
my $ant_sent;
my $wf_token;
foreach my $wf ($naf_root->findnodes('//wf'))
{
    my $wf_sent = $wf->getAttributeNode('sent')->textContent;
    my $wf_id = $wf->getAttributeNode('id')->textContent;
    $wf_id=~s/^w//;
    my $wf_word = $wf->textContent;
    if ($wf_sent ne $ant_sent)
    {
        $wf_token=1;
    }

    $words->{$wf_id}->{sent} = $wf_sent;
    $words->{$wf_id}->{token} = $wf_token;
    $words->{$wf_id}->{word} = $wf_word;
    
    $words->{$wf_id}->{parent} = "0";
    $words->{$wf_id}->{dep} = "ROOT";
    $words->{$wf_id}->{ispred} = "_";
    $words->{$wf_id}->{pred} = "_";
    
    $wf_token++;
    $ant_sent = $wf_sent;
}


my $terms;
foreach my $term ($naf_root->findnodes('//term'))
{
    my $term_id = $term->getAttributeNode('id')->textContent;
    my $term_lemma = $term->getAttributeNode('lemma')->textContent;
    my $term_pos = $term->getAttributeNode('pos')->textContent;
    #my $term_morpho = $term->getAttributeNode('morphofeat')->textContent;
    my $term_morpho = "nil";

    if($term_lemma eq ""){
	$term_lemma = "un";
    }
    if($term_lemma =~ / /){
	$term_lemma =~ s/ /_/g;
    }
    if($term_pos eq ""){
	$term_pos eq "un";
    }

    $term_pos =~ s/ /_/g;


    foreach my $target ($term->findnodes('.//target'))
    {
        my $target_id = $target->getAttributeNode('id')->textContent;
        $target_id=~s/^w//;
        $words->{$target_id}->{lemma} = $term_lemma;
        $words->{$target_id}->{pos} = $term_morpho;
        
        $terms->{$term_id} = $target_id;
    }
}


foreach my $dep ($naf_root->findnodes('//deps/dep'))
{
    my $dep_from = $dep->getAttributeNode('from')->textContent;
    my $dep_from_word = $terms->{$dep_from};
    my $dep_to = $dep->getAttributeNode('to')->textContent;
    my $dep_to_word = $terms->{$dep_to};
    my $dep_rfunc = $dep->getAttributeNode('rfunc')->textContent;
 
    if($dep_rfunc eq "-- / --"){
	$dep_rfunc = "un";
    }

    $words->{$dep_to_word}->{parent} = $words->{$dep_from_word}->{token};
    $words->{$dep_to_word}->{dep} = $dep_rfunc;
}


my $predicates;
foreach my $srl ($naf_root->findnodes('//srl/predicate'))
{
    my $predicate = "";
    my @predicateL = $srl->findnodes('./externalReferences/externalRef');
    for (my $i=0; $i<@predicateL; $i++){
	if (defined($predicateL[$i]->getAttributeNode('resource')) && $predicateL[$i]->getAttributeNode('resource')->textContent eq "PropBank"){
	    $predicate = $predicateL[$i]->getAttributeNode('reference')->textContent;
	}
    }

    #my $predicate = $srl->findnodes('./externalReferences/externalRef')->get_node(1)->getAttributeNode('reference')->textContent;
    
    if ($predicate =~ / /){
	$predicate =~ s/ /_/;
    }

    my $pred_sent;
    my $pred_token;
    
#foreach my $predicate_target ($srl->findnodes('./span/target'))
    #{
    my $predicate_target = $srl->findnodes('./span/target')->get_node(1);
    my $predicate_id = $predicate_target->getAttributeNode('id')->textContent;
    my $predicate_word = $terms->{$predicate_id};
    
    if ($predicate eq ""){
	$predicate = $words->{$predicate_word}->{lemma}.".01";
    }

    $words->{$predicate_word}->{ispred} = "Y";
    $words->{$predicate_word}->{pred} = $predicate;
    
    $pred_sent = $words->{$predicate_word}->{sent};
    $pred_token = $words->{$predicate_word}->{token};
    
    $predicates->{$pred_sent}->{$pred_token}->{pred} = $predicate;
    #}
    
    foreach my $role ($srl->findnodes('./role'))
    {
        my $semRole = $role->getAttributeNode('semRole')->textContent;
	if ($ARGV[2] eq "fullspan")
	{
	    foreach my $target ($role->findnodes('./span/target'))
	    {

		my $filler_id = $target->getAttributeNode('id')->textContent;
		my $filler_word = $terms->{$filler_id};
        
		$predicates->{$pred_sent}->{$pred_token}->{args}->{$filler_word} = $semRole;
	     
	    }
	}
	else
	{
	    my $filler_id = "";
	    my @filler_id_list = $role->findnodes('./span/target[@head="yes"]');
	    for (my $i=0; $i<@filler_id_list; $i++){
		if(defined($filler_id_list[$i]->getAttributeNode('head'))){
		    $filler_id = $filler_id_list[$i]->getAttributeNode('id')->textContent;
		}
	    }
	    if ($filler_id eq ""){
		$filler_id =  $role->findnodes('./span/target')->get_node(1)->getAttributeNode('id')->textContent; 
	    }

	    #my $filler_id = $role->findnodes('./span/target[@head="yes"]')->get_node(1)->getAttributeNode('id')->textContent;
        my $filler_word = $terms->{$filler_id};
        
        $predicates->{$pred_sent}->{$pred_token}->{args}->{$filler_word} = $semRole;
	}
    }
}

open(OUT,">:encoding(UTF-8)",$ARGV[1]);
my $ant_sent;
foreach my $wf_id (sort {$a<=>$b} keys %{ $words })
{
    my $sent = $words->{$wf_id}->{sent}; 
    my $token = $words->{$wf_id}->{token};
    my $word = $words->{$wf_id}->{word};
    my $lemma = $words->{$wf_id}->{lemma};
    my $pos = $words->{$wf_id}->{pos};
    my $parent = $words->{$wf_id}->{parent};
    my $dep = $words->{$wf_id}->{dep};
    my $ispred = $words->{$wf_id}->{ispred};
    my $pred = $words->{$wf_id}->{pred};

    if ($ant_sent ne "" && $ant_sent ne $sent)
    {
        print OUT "\n";
    }
    $ant_sent = $sent;
    print OUT $token."\t".$word."\t".$lemma."\t".$lemma."\t".$pos."\t".$pos."\t_\t_\t".$parent."\t".$parent."\t".$dep."\t".$dep."\t".$ispred."\t".$pred;
    foreach my $pred_token (sort {$a<=>$b} keys %{ $predicates->{$sent} })
    {   
        if (exists $predicates->{$sent}->{$pred_token}->{args}->{$wf_id})
        {
            print OUT "\t".$predicates->{$sent}->{$pred_token}->{args}->{$wf_id};
        }
        else
        {
            print OUT "\t_";
        }
    }
    print OUT "\n";
}
print OUT "\n";
close(OUT);
