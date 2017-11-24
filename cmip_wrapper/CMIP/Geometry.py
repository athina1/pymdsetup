#!/usr/bin/perl
#
# $Date: 2006/10/31 13:51:01 $
# $Id: Geometry.pm,v 1.2 2006/10/31 13:51:01 gelpi Exp $
# $Revision: 1.2 $
#
package Geometry;
use Geometry::Point;
1;

sub suma {
 my ($a,$b)=@_;
 return point->new (
 $a->x + $b->x,
 $a->y + $b->y,
 $a->z + $b->z);
};

sub prod {
 my ($a,$v) = @_;
 return point->new(
 $a->x * $v,
 $a->y * $v,
 $a->z * $v);
};

sub dot {
 my ($a,$b)=@_;
 return ($a->x*$b->x+
         $a->y*$b->y+
         $a->z*$b->z);
};

sub cosang {
 my ($a,$b)=@_;
 return ($a->dot($b)/($a->module()*$b->module()));
};

sub calcDist2 {
 my ($a,$b)=@_;
 return (($a->x-$b->x)**2+($a->y-$b->y)**2+($a->z-$b->z)**2);
};

sub calcDist {
 my ($a,$b)=@_;
 return sqrt(calcDist2($a,$b));
};





   

