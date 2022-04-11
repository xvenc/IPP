# Documentation of project implementation for 2. task IPP 2021/2022

Name and surname: Vaclav Korvas

Login: xkorva03

## Task

The main goal was to write two scripts `interpret.py` and `test.php`. The first script loads input code in XML format and interprets the instructions and the second script is used to automatic test the `parse.php` and `interpret.py` scripts.

### interpret.py

The implementation is devided into two separate files. Main file `interpret.py` and file with the implementation of individual classes `classes.py`.

#### classes.py

`XML_checker` class is used to checked if the input XML is well-formated. Then it checks if correct header is present and if only allowed attributes and oppcodes are used. Then intstuctuctions are read into a list in function `read_instructions`. To store information about instructions, class `Instruction` is used. ``Instruction`` class is used to store information about used instructions such as its opcode, list of arguments and order of the instruction. To store informations about instruction arguments, class `Argument` is used. About each instruction argument is stored its type (string, int, bool, nil), its value, and order. If the type is string then all escape sequencies are converted to characters.

#### Implementation of interpret.py

In the main code I go through all the instruction three times. First time I cycle through the instruction list in function `check_argument_types` to make sure when *symb* is expected *var* isn't used. The second time I go through all instructions is in function `find_labels` to find all labels and check if the labels are not redefined. The third times is to interpret individual instructions. This is done in function `interpret`. Here is one big "if-else tree" which will determine which instruction will be interpreted. This is run in a loop through all the instructions used in the code. At the beginning of the loop function `get_data_from_arg` is called. This function is used to extract values from frames and constant data from given instruction arguments.
For example if we have instruction *ADD GF@count int@40 int@2* then the functions look if variable *count* is defined in global frame and reads its value and stores it into variable *data_first* and also stores values 40 and 2 into variables(*data_second*, *data_third*). These variables are used later in interpreting given instrusction. And at the end of the loop is called function `write_to_frame` which writes data into given variable in given frame.

### test.php

TODO
