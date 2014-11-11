#!/usr/bin/env perl
use strict;
use warnings;

my $input = $ARGV[0] or die "File with URIs that should be extracted needed as parameter.\n";

my $file = 'all-geonames-rdf.txt';

open(my $ifh, $input) or die "Could not open $input: $!\n";
my @input = <$ifh>;

open(my $info, $file) or die "Could not open $file: $!\n";

my $dump = '';

while( my $line = <$info>)  {
        if ($dump) {
            print STDERR "Writing file $dump to disk.\n";
            open(my $oh, '>', $dump) or die "Could not open $dump for writing.\n";
            print $oh $line;
            $dump = '';
        }
        if ($line =~ /^http:\/\/sws.geonames.org\/(\d*)\/$/) {
            if (grep { $_ eq $line } @input) {
                # todo: remove $line from @input
                $dump = "$1.rdf";
            }
        }
}

close $info;
