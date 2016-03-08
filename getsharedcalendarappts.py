''' Get items from a shared outlook calendar that you have access to.'''

import csv
import datetime
import win32com.client

class SharedCalendarSurrogate(object):
  ''' '''

  def __init__(self, recipient):
    ''' '''
    outlook = win32com.client.Dispatch('Outlook.Application')
    namespace = outlook.GetNamespace('MAPI')
    recipient = namespace.createRecipient(recipient)
    resolved = recipient.Resolve()
    if resolved:
        self.shared_calendar = namespace.GetSharedDefaultFolder(recipient, 9)
    else:
        raise ValueError('recipient could not be resolved.')

  def get_appointments(self):
    ''' '''
    self.appointments = self.shared_calendar.Items

  def sort_appointments(self):
    ''' '''
    # TODO add more sort options
    self.appointments.sort('[Start]')

  def include_recurrences(self):
    ''' '''
    self.appointments.IncludeRecurrences = 'True'

  def filter_appointments(self, filter_string):
    ''' '''
    self.filter_string = filter_string
    self.appointments = self.appointments.Restrict(filter_string)

  def filter_appointments_by_date_range(self, date_range, delimiter='-'):
    ''' '''
    dates = [datetime.datetime.strptime(date, '%m/%d/%Y') for date in date_range.split(delimiter)]
    begin = datetime.datetime.strftime(min(dates), '%m/%d/%Y')
    end = datetime.datetime.strftime(max(dates), '%m/%d/%Y')
    filter_string = "[Start] >= '%s' AND [End] <= '%s'" % (begin, end)
    self.filter_appointments(filter_string)

  def filter_appointments_by_date(self, date, property_='Start', operator='='):
    ''' '''
    filter_string = "[%s] %s '%s'" % (property_, operator, date)
    self.filter_appointments(filter_string)

  def filter_appointments_by_organizer(self, organizer):
    ''' '''
    filter_string = "[Organizer] = '%s'" % (organizer)
    self.filter_appointments(filter_string)

  def filter_appointments_by_organizers(self, organizers):
    ''' '''
    organizer_filter_string = "[Organizer] = '%s'"
    filter_string = ' Or '.join((organizer_filter_string % (organizer) for organizer in organizers))
    self.filter_appointments(filter_string)

  def generate_appointment_details(self):
    ''' '''
    self.appointment_details = ((appointment.Start, appointment.End, appointment.Organizer, appointment.Subject.encode('utf-8'),
                            appointment.Body.encode('utf-8')[:32758])
                            for appointment in self.appointments)

    # TODO add more export format options.
  def export_to_csv(self, file):
    ''' '''
    with open(file, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(self.appointment_details)

# TODO
class FilterString(object):
  ''' '''

  def __init__(self):
    ''' '''

  def add_property(self):
    ''' '''

  def build(self):
    ''' '''

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipient', help='the shared calendar you want to pull appointments from.')
    parser.add_argument('-b', '--begin', help='include appointments on or after the begin date.')
    parser.add_argument('-e', '--end', help='include appointments on or before the end date.')
    parser.add_argument('-o', '--organizer', help='include appoinments from the organizer.')
    parser.add_argument('-r', '--daterange', help='include appointments within the date range.')
    parser.add_argument('--includerecurrences', help='include recurrences')
    args = parser.parse_args()

    shared_calendar = SharedCalendarSurrogate(recipient=args.recipient)
    shared_calendar.get_appointments()
    if args.includerecurrences == True:
      shared_calendar.include_recurrences()
    shared_calendar.sort_appointments()
    if args.daterange:
      shared_calendar.filter_appointments_by_date_range(date_range=args.daterange)
    if args.organizer:
      shared_calendar.filter_appointments_by_organizer(organizer=args.organizer)
    shared_calendar.generate_appointment_details()
    shared_calendar.export_to_csv('%s_appointments.csv' % args.recipient)
