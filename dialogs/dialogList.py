from dialogs import (
    basic_dialogs,
    messages_dialogs,
    measurments_dialogs,
    medicine_dialogs,
)


dialogs_list = [
    basic_dialogs.TimeDialog,
    basic_dialogs.SetVolumeDialog,
    basic_dialogs.HelpDialog,
    messages_dialogs.NewMessagesDialog,
    messages_dialogs.SendMessageDialog,
    measurments_dialogs.AddValueDialog,
    measurments_dialogs.CommitFormsDialog,
    medicine_dialogs.CheckMedicinesDialog,
    medicine_dialogs.CommitMedicineDialog,
]
