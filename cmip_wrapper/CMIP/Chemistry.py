#
# $Date: 2006/10/31 13:51:01 $
# $Id: Chemistry.pm,v 1.2 2006/10/31 13:51:01 gelpi Exp $
# $Revision: 1.2 $
#
package Chemistry;

use Chemistry::Atom;
use Chemistry::Residue;
use Chemistry::Molecule;
use Chemistry::ForceField;
use Chemistry::AtomType;
use Chemistry::Chain;
1;

sub loadForceField {
	my $fn = shift;
	my $fftxt=`cat $fn` || die "$fn not found";
	my $ff = ForceField->load($fftxt);
	return $ff;
};

sub loadPDB {
	my ($fn, $id, $ff) = @_;
	my $fntxt = `cat $fn`;
	return Molecule->loadPDBSimple($id, $fntxt, $ff);
};
sub loadHET {
	my ($fn, $ff) = @_;
	my $fntxt = `cat $fn`;
	return Molecule->loadHETSimple($fntxt, $ff);
};
		
		
	
