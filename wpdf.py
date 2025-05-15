import sys
import fitz  # PyMuPDF
import argparse


class PDFViewerCLI:
    def __init__(self, pdf_file):
        self.pdf_document = fitz.open(pdf_file)
        self.current_page = 0
        self.total_pages = self.pdf_document.page_count
        self.pdf_file = pdf_file

    def show_page(self, page_number):
        """Display the given page number."""
        if 0 <= page_number < self.total_pages:
            page = self.pdf_document.load_page(page_number)
            text = page.get_text("text")  # Extract page text
            print(f"\n--- Page {page_number + 1}/{self.total_pages} ---")
            print(text)
            print("\n" + "-" * 40)
        else:
            print(f"Invalid page number. Please provide a number between 1 and {self.total_pages}.")

    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page(self.current_page)
        else:
            print("You are already on the last page.")

    def previous_page(self):
        """Go to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)
        else:
            print("You are already on the first page.")

    def go_to_page(self, page_number):
        """Go to a specific page."""
        if 0 <= page_number < self.total_pages:
            self.current_page = page_number
            self.show_page(self.current_page)
        else:
            print(f"Invalid page number. Please provide a number between 1 and {self.total_pages}.")

    def close(self):
        """Close the PDF document."""
        self.pdf_document.close()
        print("PDF closed.")


def main():
    parser = argparse.ArgumentParser(description="CLI PDF Viewer")
    parser.add_argument("pdf_file", help="Path to the PDF file", nargs="?")
    parser.add_argument("--page", type=int, default=1, help="Page number to start from (default: 1)")
    parser.add_argument("--n", action="store_true", help="Trigger the Easter egg")

    args = parser.parse_args()

    # Easter egg handling
    if args.n:
        print("Back it up. Back it up, back it up.")
        sys.exit(0)

    # Check if the PDF file is provided
    if not args.pdf_file:
        print("Error: Please provide a PDF file.")
        sys.exit(1)

    pdf_file = args.pdf_file
    start_page = args.page - 1  # Convert to 0-indexed

    try:
        viewer = PDFViewerCLI(pdf_file)

        # Start from the specified page
        viewer.go_to_page(start_page)

        while True:
            command = input("\nCommands: [n] Next, [p] Previous, [g] Go to page, [q] Quit\n> ").strip().lower()

            if command == "n":
                viewer.next_page()
            elif command == "p":
                viewer.previous_page()
            elif command == "g":
                try:
                    page_number = int(input("Enter page number: ")) - 1  # Convert to 0-indexed
                    viewer.go_to_page(page_number)
                except ValueError:
                    print("Invalid input. Please enter a valid page number.")
            elif command == "q":
                viewer.close()
                break
            else:
                print("Invalid command. Please try again.")

    except FileNotFoundError:
        print(f"Error: File '{pdf_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()