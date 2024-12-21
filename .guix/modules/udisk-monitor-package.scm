(define-module (udisk-monitor-package)
  #:use-module (guix)
  #:use-module (guix git-download)   ;for ‘git-predicate’
  #:use-module (guix build-system pyproject)
  #:use-module (gnu packages glib)
  #:use-module (gnu packages python-build)
  #:use-module (gnu packages freedesktop)
  #:use-module ((guix licenses) #:prefix license:)
  )

(define vcs-file?
  ;; Return true if the given file is under version control.
  (or (git-predicate (dirname (dirname (current-source-directory))))
      (const #t)))                                ;not in a Git checkout

(define-public udisk-monitor
  (package
    (name "udisk-monitor")
    (version "0.0.1-git")                          ;funky version number
    (build-system pyproject-build-system)
    (source (local-file "../.." "guile-checkout"
                        #:recursive? #t
                        #:select? vcs-file?))
    (arguments
     (list
      #:tests? #false
      #:phases
      #~(modify-phases %standard-phases
          (add-after 'wrap 'gi-wrap
            (lambda _
              (let ((prog (string-append #$output "/bin/udisk_monitor")))
                (wrap-program prog
                  `("GI_TYPELIB_PATH" = (,(getenv "GI_TYPELIB_PATH"))))))))))
    (native-inputs
     (list
      python-setuptools
      python-wheel))

    (inputs
     (list
      python-pygobject
      glib
      udisks))

    (synopsis "A small daemon for removable media")
    (description "A small daemon that monitors udisk for the registration and mounting of a certain filesystem.")
    (home-page "https://github.com/michaelglas/udisk_monitor")
    (license license:gpl3+)))

udisk-monitor
