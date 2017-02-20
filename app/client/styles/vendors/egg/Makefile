SCSS = docs/egg.scss docs/styles.scss
CSS = docs/egg.css docs/styles.css

.PHONY: all clean

all: clean $(CSS)

$(CSS): $(SCSS)
	sass --sourcemap=none --style compressed $<:$@

clean:
	rm -f $(CSS)
