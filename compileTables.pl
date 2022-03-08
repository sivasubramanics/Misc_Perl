#!/usr/bin/env perl
# name            :compileTable.pl
# description     :This script will help the user to combine the ortholog gene annotations from individual organism files.
# author          :siva.selvanayagam@wur.nl
# date            :2022/03/08
# version         :0.1
# usage           :perl combineTable <geneIDs_pestgroups_rename.txt> <org1_annotation.txt> <org2_annotation.txt> <org3_annotation.txt> ...
# notes           :
# perl_version    :5.26.1
# ==============================================================================

# USAGE: perl compileTables.pl geneIDs_pestgroups_rename.txt Autographa_go_annotations_rename.txt Exigua_GO_annotations_rename.txt Littoralis_go_annotations_rename.txt Mamestra_go_annotations_rename.txt Trichoplusia_GO_annotations_rename.txt

if ($ARGV[1] eq ""){
  die "perl combineTable <geneIDs_pestgroups_rename.txt> <org1_annotation.txt> <org2_annotation.txt> <org3_annotation.txt> ...\n";
}
$og_file = $ARGV[0]; # Input gene OG group file 
$out_file = "processed_go_file.txt"; # Output file name (edit this for prefered file name)

# Adding the gene list and its correstponding GO terms into one BIG hash 
%org_hash;
for ($i=1;$i<=$#ARGV;$i++){
  $org_file = $ARGV[$i];
  print "Hashing the file: $org_file\n";
  ($org, $tmp_hash) = &get_org_hash($org_file); # processing organism specific file through subroutine
  if(!exists $org_hash{$org}){
    $org_hash{$org};
  }
  $org_hash{$org}=\%$tmp_hash;
  print "Number of entires: ",scalar(keys(%org_hash)),".",$org,"\t",scalar(keys(%{$org_hash{$org}})),"\n";
}

# reading ortho group file (geneIDs_pestgroups_rename.txt) line-by-line and writing outputs
open(FA, $og_file);
# creating output file
open(OUT, ">$out_file");
while(<FA>){
  chomp();
  # spliting the line with space (or continous space)
  @arr = split(/\s+/, $_);
  $out_string = "";
  # for each gene/isoform name (leaving first element of arr)
  for($i=1;$i<=$#arr;$i++){
    # getting the organism identifier from gene/isoform name. This will work only if organism identifier is of only 2 alphabets. If its a different format then change the below condition
    if($arr[$i] =~ /^TRINITY_(\w\w)_/){
      $org = $1;
    }
    if(exists $org_hash{$org}){
      # if we have the isoform in the BIG hash
      if(exists $org_hash{$org}{$arr[$i]}){
        if($out_string eq ""){
          $out_string .= $arr[$i]."-".$org_hash{$org}{$arr[$i]};
        }
        else{
          $out_string .= "\t".$arr[$i]."-".$org_hash{$org}{$arr[$i]};
        }
      }
      # if we DON"T have the isoform in the BIG hash
      else{
        if($out_string eq ""){
          $out_string .= $arr[$i]."-"."NA";
        }
        else{
          $out_string .= "\t".$arr[$i]."-"."NA";
        }
      }
    }
  }
  # write the line on output file handle
  print OUT $arr[0],"\t",$out_string,"\n";
}
# and DON'T EVER FORGET to close the file handles
close OUT;
close FA;

# subroutine to process the organism files
sub get_org_hash(){
  $file_name = shift(@_); # organism filename
  open(FA, $file_name);
  $prev_org = "";
  $org = "";
  %hash;
  while(<FA>){
    chomp();
    @arr = split(/\s+/, $_);
    # getting the organism identifier from gene/isoform name. This will work only if organism identifier is of only 2 alphabets. If its a different format then change the below condition
    if($arr[0] =~/^TRINITY_(\w\w)_/){
      $org = $1;
    }
    else{
      print "Skipping the gene: $arr[0]\n";
      next;
    }
    if ($org ne $prev_org && $prev_org ne ""){
      die "$file_name contains multiple organisms. Exiting..! $org\n";
    }
    $hash{$arr[0]} = $arr[1];
    $prev_org = $org;
  }
  close FA;
  return $org, \%hash;
}