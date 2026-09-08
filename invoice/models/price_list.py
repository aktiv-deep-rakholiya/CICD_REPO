from  odoo import models ,fields ,api ,  _
from odoo.exceptions import UserError


class PriceList(models.Model):
    _name = 'price.list'
    _description = "Price List"
    _rec_name = 'pos'

    client_id = fields.Many2one('client.master',string="Client")

    @api.depends('client_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_id:
                rec.client_name = rec.client_id.client_name
            else:
                rec.client_name = False

    client_name= fields.Selection([
        ('tcm', 'Tecnimont'),
        ('petrofac', 'Petrofac'),
        ('ace', 'ACE Plantech'),
        ('eneico', 'Eneico'),
        ('edif', 'Edif NDE'),
        ('equasrl', 'Equa SRL'),
        ('lindinger', 'Lindinger USA'),
        ('spxflow', 'Dollinger Filtration Limited'),
        ('global', 'Global SCS'),
        ('tecnicas','Tecnicas Reunidas'),
        ('tecton','Tecton'),
        ('arotec','Arotec'),
        ('clatech','Clatech Consulting Co.Ltd'),
        ('sisisrl','SISI SRL'),
        ('stamicarbon','STAMICARBON'),
        ('jkinspection','JK Inspection Engineering co ltd'),
        ('monarch','Monarch Style'),
        ('inspectorunion','Inspectors Union Co.'),
        ('swissapproval','Swiss Approval Team'),
        ('neilbarnett','Neil Barnett Inspection Services'),
        ('applus','Applus Velosi'),
        ('enzone','Enzone'),
        ('bureau','BUREAU Technical Services'),
        ('unitedglobal','United Global'),
        ('teleios','Teleios Spexxa Engg and Cons'),
        ('phbweser','PHB Weserhutte'),
        ('apollo', 'Apollo Electromechanical Contracting LLC'),
        ('eurture', 'Eurtrue'),
        ('others', 'Others')
        
    ], string='Client Selection' ,default="tcm", compute='compute_client_name'
    )

    pos =fields.Integer(string="POS")

    country =fields.Many2one('res.country',string='Country')

    cat_location= fields.Selection([
        ('vendorfacility', 'Vendor Facility/ Loading Unloading Location'),
        ('remote', 'Remote Expediting - With Agency Tool'),
        ('remote2', 'Remote Expediting - With Third Parties Tool'),
        ('companyoffice', 'Company Office'),     
        ], string='Location', readonly=False, copy=False, index=True)

    services = fields.Selection([
        ('logistics', 'Logistics'),
        ('expediting', 'Expediting & Scheduling'),
        ('inspection', 'Inspection'),   
        ], string='Services', readonly=False, copy=False, index=True)

    employee_role = fields.Many2one('p4.employee.role', string='Role')

    oncall= fields.Char(string="OnCall-1 to19-DayExp")

    resident1= fields.Char(string="Resident1- 20to27-Day Exp")
    resident2= fields.Char(string="Resident2- 28to78-Day Exp")
    resident3= fields.Char(string="Resident3- 79to156-Day Exp")
    resident4= fields.Char(string="Resident4- 157to312-Day Exp")

    oncall_without_night= fields.Char(string="OnCall-Add Exp-without overnight stay")
    oncall_with_night= fields.Char(string="OnCall-Add Exp-with overnight stay")
    oncall_without_night1= fields.Char(string="OnCall-1 to19-without overnight stay")
    oncall_with_night1= fields.Char(string="OnCall-1 to19-with overnight stay")

    resident_without_night_1= fields.Char(string="Resident1- 20to27-without overnight stay")
    resident_with_night_1= fields.Char(string="Resident1- 20to27-with overnight stay")

    resident_without_night_2= fields.Char(string="Resident2- 28to78-without overnight stay")
    resident_with_night_2= fields.Char(string="Resident2- 28to78-with overnight stay")

    resident_without_night_3= fields.Char(string="Resident3-79to156-without overnight stayt stay")
    resident_with_night_3= fields.Char(string="Resident3-79to156-with overnight stayt stay")

    resident_without_night_4= fields.Char(string="Resident4- 157to312-Day Exp-without overnight stayt stay")
    resident_with_night_4= fields.Char(string="Resident4- 157to312-Day Exp-with overnight stayt stay")

    remote_call= fields.Char(string="RemoteCall-Reduction-Day")
    exp_remote= fields.Char(string="ExpRemote Call-HalfDayExp")

    def action_excelupload(self):
    	return {
			'type': 'ir.actions.act_window',
			'name': 'Upload File',
			'res_model': 'upload.wizard',
			'view_mode': 'form',
			'target': 'new',
		}

    def action_excelupload1(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload File',
            'res_model': 'upload.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
