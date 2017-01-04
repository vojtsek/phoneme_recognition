all: sclite
	bash -c "source env/bin/activate; pip install SpeechRecognition"
	@echo "sclite installed, all ready"

sclite: sclite_compiled

.PHONY: sclite_compiled
sclite_compiled: sctk sctk_configured
	cd sctk; \
	$(MAKE) all && $(MAKE) install && $(MAKE) doc

sctk_configured: sctk sctk/.configured

sctk/.configured: sctk
	cd sctk; $(MAKE) config
	touch sctk/.configured

.PHONY: sctk
sctk: sctk-2.4.10-20151007-1312Z.tar.bz2
	tar xojf sctk-2.4.10-20151007-1312Z.tar.bz2
	rm -rf sctk && ln -s sctk-2.4.10 sctk

sctk-2.4.10-20151007-1312Z.tar.bz2:
	wget -T 10 -t 3 ftp://jaguar.ncsl.nist.gov/pub/sctk-2.4.10-20151007-1312Z.tar.bz2|| \
	wget --no-check-certificate -T 10 http://www.openslr.org/resources/4/sctk-2.4.10-20151007-1312Z.tar.bz2
