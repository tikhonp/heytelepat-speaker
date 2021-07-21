from events import messages_events, measurements_events, medicines_events


events_list = [
    messages_events.MessageNotificationEvent,
    measurements_events.MeasurementNotificationEvent,
    medicines_events.MedicineNotificationEvent,
]
