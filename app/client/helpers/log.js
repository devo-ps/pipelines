export function highlightLog(input) {
  var timestampRegex = /(\d\d\d\d:\d\d:\d\d) (\d\d:\d\d:\d\d):/g;
  var failRegex = /([1-9] failed|failed|fail|error|err|status: 1)/g;
  var succRegex = /(0 failed|status: 0|success)/g;
  var bashColors = [
    [/\[(0;)?30m(.*?)\[(0)?m/g, '<span class="black">$2</span>'],
    [/\[(0;)?31m(.*?)\[(0)?m/g, '<span class="red">$2</span>'],
    [/\[(0;)?32m(.*?)\[(0)?m/g, '<span class="green">$2</span>'],
    [/\[(0;)?33m(.*?)\[(0)?m/g, '<span class="brown">$2</span>'],
    [/\[(0;)?34m(.*?)\[(0)?m/g, '<span class="blue">$2</span>'],
    [/\[(0;)?35m(.*?)\[(0)?m/g, '<span class="purple">$2</span>'],
    [/\[(0;)?36m(.*?)\[(0)?m/g, '<span class="cyan">$2</span>'],
    [/\[(0;)?37m(.*?)\[(0)?m/g, '<span class="light-gray">$2</span>'],
    [/\[1;30m(.*?)\[0m/g, '<span class="dark-gray">$1</span>'],
    [/\[1;31m(.*?)\[0m/g, '<span class="light-red">$1</span>'],
    [/\[1;32m(.*?)\[0m/g, '<span class="light-green">$1</span>'],
    [/\[1;33m(.*?)\[0m/g, '<span class="yellow">$1</span>'],
    [/\[1;34m(.*?)\[0m/g, '<span class="light-blue">$1</span>'],
    [/\[1;35m(.*?)\[0m/g, '<span class="light-purple">$1</span>'],
    [/\[1;36m(.*?)\[0m/g, '<san class="light-cyan">$1</span>'],
    [/\[1;37m(.*?)\[0m/g, '<span class="white">$1</span>'],
  ]
  bashColors.map(function(code) {
    input = input.replace(code[0], code[1])
  })

  if (input !== undefined) {
    input = input.replace(timestampRegex, '<time class="time">$2</time>')
    input = input.replace(failRegex, '<span class="red">$1</span>')
    input = input.replace(succRegex, '<span class="green">$1</span>')
  }
  return input;
};
