import datetime
from textual import log
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, ListView, Button, Static, ListItem, Label, Input
from textual.containers import Horizontal, Vertical, HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message
from .ebook_merger_service import EbookMergerService
import sys
import traceback
import os

class EpubToSelectItemWidget(Widget):
    # epub_item = reactive({})

    DEFAULT_CSS = """
        EpubToSelectItemWidget {
            height: auto
        }
        EpubToSelectItemWidget Horizontal {
            height: auto
        }
        EpubToSelectItemWidget Label {
            width: 1fr
        }
        EpubToSelectItemWidget Button {
            padding: 0
        }

    """

    class Selected(Message):
        def __init__(self, selected_epub_item):
            super(EpubToSelectItemWidget.Selected, self).__init__()
            self.selected_epub_item = selected_epub_item

    def __init__(self, epub_item,):
        super().__init__()
        self.epub_item = epub_item

    def compose(self):
        item = self.epub_item
        yield Horizontal(
            Label(item.get('name')),
            Label(item.get('sequence')),
            Button(">>")
        )

    def on_button_pressed(self, event):
        self.post_message(self.Selected(self.epub_item))

class EpubSelectedItemWidget(Widget):
    # epub_item = reactive({})

    DEFAULT_CSS = """
    EpubSelectedItemWidget {
        height: auto
    }
    EpubSelectedItemWidget Horizontal {
        height: auto
    }
    EpubSelectedItemWidget Label {
        width: 1fr
    }
    EpubSelectedItemWidget Button {
        padding: 0
    }

    """

    def __init__(self, index, epub_item,):
        super().__init__()
        self.epub_item = epub_item
        self.index = index

    def compose(self):
        item = self.epub_item
        yield Horizontal(
            Label(item.get('name')),
            Button("Up", id='button_up'),
            Button("Down", id='button_down'),
            Button("Remove", id='button_remove'),
        )

    class Event(Message):
        def __init__(self, type, index, epub_item, ):
            super(EpubSelectedItemWidget.Event, self).__init__()
            self.type = type
            self.index = index
            self.epub_item = epub_item

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        type = button_id
        if button_id == 'button_up':
            type = 'up'
        elif button_id == 'button_down':
            type = 'down'
        elif button_id == 'button_remove':
            type = 'remove'
        else:
            pass

        log("Button Inner Press ", type)
        self.post_message(
            self.Event(
                type=type,
                epub_item=self.epub_item,
                index=self.index
            )
        )

class EbookMergerApp(App):
    """A Textual app to manage stopwatches."""
    CSS_PATH = './ebook_merger_style.tcss'

    data = reactive({})
    all_keys = reactive([], recompose=True)
    selected_keys = reactive([], recompose=True)

    export_book_name = reactive("")

    def __init__(self, opts, *args, **kwargs):
        res = super(EbookMergerApp, self).__init__(*args, **kwargs)
        self.opts = opts
        self.service = EbookMergerService(opts=opts)

    def on_epub_selected_item_widget_event(self, event: EpubSelectedItemWidget.Event):
        log("Event Butto UP Down " )
        index = event.index
        to_swap = index

        if event.type in ['up', 'down']:
            if event.type == 'up':
                to_swap = index - 1
            elif event.type == 'down':
                to_swap = index + 1
            else:
                pass

            if to_swap < 0:
                to_swap = 0
            if to_swap >= len(self.selected_keys):
                to_swap = len(self.selected_keys) - 1

            self.selected_keys[index], self.selected_keys[to_swap] = self.selected_keys[to_swap], self.selected_keys[index]
            self.mutate_reactive(EbookMergerApp.selected_keys)
        if event.type == 'remove':
            self.selected_keys.pop(index)
            self.mutate_reactive(EbookMergerApp.selected_keys)

    def _fatal_error(self) -> None:
        log("Got Error =====================", traceback.format_exc())

        super()._fatal_error()
        _, exception, _ = sys.exc_info()

        if exception is not None:
            raise exception

    def _get_key_from_epub_item(self, epub_item):
        return epub_item.get('name')

    # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]\
    def on_mount(self):
        log(f"serservice ",self.service)
        # try:

        epub_files = self.service._list_epub_in_directory()
        # epub_files.sort(key=lambda epub_item:  self._get_key_from_epub_item(epub_item))
        self.data = {
            item.get('name'): item
            for item in epub_files
        }
        self.all_keys = [
            self._get_key_from_epub_item(epub_item)
            for epub_item in epub_files
        ]
        self.selected_keys = []
        self.mutate_reactive(EbookMergerApp.all_keys)
     
        pass

    # EPubToSelectItemWidget
    def on_epub_to_select_item_widget_selected(self, event: EpubToSelectItemWidget.Selected):
        selected_epub_item = self._get_key_from_epub_item(event.selected_epub_item)
        self.selected_keys += [selected_epub_item]
        # self.recompose()
        self.mutate_reactive(EbookMergerApp.selected_keys)

    def watch_selected_keys(self):
        log("Watch on Selected Key ", self.selected_keys)
        # if self.selected_keys:
        # log("MErge Query ", merge_name_input)

        selected_keys = self.selected_keys
        if selected_keys and not self.export_book_name:

            first_key = selected_keys[0]
            epub_item = self.data[first_key]

            self.export_book_name = epub_item.get('name')
            # merge_name_input.

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        log("View Al l KEy ", self.data)
        log("View Al l eky s ", self.all_keys)

        unselected_keys = [
            key
            for key in self.all_keys
            if key not in self.selected_keys
        ]
        unselected_list_items_widget = [
            ListItem(
                EpubToSelectItemWidget(epub_item=self.data[key])
            )
            for key in unselected_keys
        ]

        selected_list_items_widget = [
            ListItem(
                EpubSelectedItemWidget(
                    index=index,
                    epub_item=self.data[key]
                )
            )
            for index, key in enumerate(self.selected_keys)
        ]

        yield Header()

        yield Horizontal(
            ListView(
                ListItem(
                    Label("Found EPUBs.", ),
                    disabled=True,
                    classes='text-center'
                ),
                *unselected_list_items_widget,
                classes='columns',
            ),

            ListView(
                ListItem(
                    Label("Merge EPUbs.",),
                    disabled=True,
                    classes='text-center'
                ),
                *selected_list_items_widget,
                classes='columns'
            )
        )

        yield Horizontal(
            Input(
                value=self.export_book_name,
                placeholder='Merge File Name',
                id='merge-input-file-name',
                classes='merge-input-file-name'
            ),
            Button(
                "Merge",
                classes='button-merged',
                id='button_merged'
            ),
            classes='merge-container'
        )

        yield Footer()

    def _action_merged(self):
        
        to_merged_epub_files = [
            self.data[key]['path']
            for key in self.selected_keys
        ]
        output_dir = self.opts.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = f'{output_dir}/{self.export_book_name}.epub'

        self.service._merge_epub_files(output_path, to_merged_epub_files)

        # close after finished
        sys.exit(0)


    def on_input_changed(self, event: Input.Changed):
        inp = event.input
        if inp.id == 'merge-input-file-name':
            self.export_book_name = inp.value 


    def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        log("Spp Buton lick ", button)
        if button.id == 'button_merged':
            button.disabled = True
            button.loading = True
            self._action_merged()
            

# if __name__ == '__main__':
#     start_time = datetime.datetime.now()
#     print('Start at : ', str(start_time))

#     main()
    
#     end_time = datetime.datetime.now()
#     print("End at : ", str(end_time))
#     print("Elapsed : ", str(end_time - start_time))