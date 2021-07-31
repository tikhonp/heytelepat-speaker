from dialogs import (
    measurments_dialogs,
    medicine_dialogs,
    messages_dialogs,
    basic_dialogs
)

dialogs_list = [
    basic_dialogs.TimeDialog,
    basic_dialogs.SetVolumeDialog,
    basic_dialogs.HelpDialog,
    basic_dialogs.ResetDialog,
    basic_dialogs.AnekDialog,
    basic_dialogs.WeatherDialog,
    messages_dialogs.NewMessagesDialog,
    messages_dialogs.SendMessageDialog,
    measurments_dialogs.AddValueDialog,
    measurments_dialogs.CommitFormsDialog,
    medicine_dialogs.CheckMedicinesDialog,
    medicine_dialogs.CommitMedicineDialog,
]
