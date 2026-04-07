import { describe, it, expect } from 'vitest'
import { regexMail, regexPassword, regexGeneric } from '@/libs/regex'
import fc from 'fast-check'

describe('regexMail', () => {
  const validEmails = [
    'user@example.com',
    'firstname.lastname@domain.org',
    'user+tag@sub.domain.co',
    'user123@test.fr',
    'a@b.cd',
    '"quoted"@example.com'
  ]

  const invalidEmails = [
    '',
    'plaintext',
    '@domain.com',
    'user@',
    'user@.com',
    'user@domain',
    'user @domain.com',
    'user@domain..com'
  ]

  it.each(validEmails)('should match valid email: %s', (email) => {
    expect(regexMail.test(email)).toBe(true)
  })

  it.each(invalidEmails)('should reject invalid email: %s', (email) => {
    expect(regexMail.test(email)).toBe(false)
  })
})

describe('regexPassword', () => {
  const validPasswords = [
    'Abcdefgh1!ab',       // exactly 12 chars, has lower, upper, digit, special
    'MyP@ssw0rd!!xx',     // 14 chars
    'Str0ng-Pass!word',   // 16 chars with hyphen
    'Test#1234abcD',      // 13 chars with #
    'aB3$aaaaaaaa',       // 12 chars minimal
    'Complex^Pass1w'      // 14 chars with ^
  ]

  const invalidPasswords = [
    'short1!A',            // too short (< 12 chars)
    'abcdefgh1!ab',        // no uppercase
    'ABCDEFGH1!AB',        // no lowercase
    'Abcdefgh!!ab',        // no digit
    'Abcdefgh123a',        // no special char
    'Abcdefgh1!a<',        // contains <
    'Abcdefgh1!a>',        // contains >
    'Abcdefgh1!a"',        // contains "
    "Abcdefgh1!a'",        // contains '
    ''                     // empty string
  ]

  it.each(validPasswords)('should match valid password: %s', (password) => {
    expect(regexPassword.test(password)).toBe(true)
  })

  it.each(invalidPasswords)('should reject invalid password: %s', (password) => {
    expect(regexPassword.test(password)).toBe(false)
  })
})

describe('regexGeneric', () => {
  const validStrings = [
    'Hello World',
    'Jean-Pierre',
    "l'hôpital",
    'Département 75',
    'éàèîâôêûù',
    'Rue de la Paix, 12',
    'Question?',
    'Attention!',
    'path/to/file',
    'under_score',
    '(parenthèses)',
    'a+b',
    'Simple'
  ]

  const invalidStrings = [
    '',                    // empty string
    'hello@world',         // contains @
    'test<html>',          // contains < >
    'price: 10€',          // contains € and :
    'semi;colon',          // contains ;
    'hash#tag'             // contains #
  ]

  it.each(validStrings)('should match valid generic string: %s', (str) => {
    expect(regexGeneric.test(str)).toBe(true)
  })

  it.each(invalidStrings)('should reject invalid generic string: %s', (str) => {
    expect(regexGeneric.test(str)).toBe(false)
  })
})

// ============================================================
// Property-Based Tests (fast-check)
// ============================================================

// Feature: frontend-test-coverage, Property 16: Validation regex email
// **Validates: Requirements 15.1**
describe('Property 16: Validation regex email', () => {
  const localPartChar = fc.mapToConstant(
    { num: 26, build: (v: number) => String.fromCharCode(97 + v) },
    { num: 26, build: (v: number) => String.fromCharCode(65 + v) },
    { num: 10, build: (v: number) => String.fromCharCode(48 + v) },
    { num: 1, build: () => '_' },
    { num: 1, build: () => '-' },
    { num: 1, build: () => '+' }
  )

  const localPartArb = fc
    .array(localPartChar, { minLength: 1, maxLength: 15 })
    .map((chars) => chars.join(''))

  const domainLabelChar = fc.mapToConstant(
    { num: 26, build: (v: number) => String.fromCharCode(97 + v) },
    { num: 10, build: (v: number) => String.fromCharCode(48 + v) }
  )

  const domainLabelArb = fc
    .array(domainLabelChar, { minLength: 1, maxLength: 10 })
    .map((chars) => chars.join(''))

  const tldArb = fc
    .array(
      fc.mapToConstant({ num: 26, build: (v: number) => String.fromCharCode(97 + v) }),
      { minLength: 2, maxLength: 6 }
    )
    .map((chars) => chars.join(''))

  const validEmailArb = fc
    .tuple(localPartArb, domainLabelArb, tldArb)
    .map(([local, domain, tld]) => `${local}@${domain}.${tld}`)

  it('should match any well-formed email (local@domain.tld)', () => {
    fc.assert(
      fc.property(validEmailArb, (email) => {
        expect(regexMail.test(email)).toBe(true)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject strings missing @ sign', () => {
    const noAtChar = fc.mapToConstant(
      { num: 26, build: (v: number) => String.fromCharCode(97 + v) },
      { num: 26, build: (v: number) => String.fromCharCode(65 + v) },
      { num: 10, build: (v: number) => String.fromCharCode(48 + v) },
      { num: 1, build: () => '.' },
      { num: 1, build: () => '-' }
    )
    const noAtArb = fc
      .array(noAtChar, { minLength: 1, maxLength: 30 })
      .map((chars) => chars.join(''))
      .filter((s) => !s.includes('@'))

    fc.assert(
      fc.property(noAtArb, (str) => {
        expect(regexMail.test(str)).toBe(false)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject strings with no domain TLD (no dot after @)', () => {
    const domainNoDotChar = fc.mapToConstant(
      { num: 26, build: (v: number) => String.fromCharCode(97 + v) },
      { num: 10, build: (v: number) => String.fromCharCode(48 + v) }
    )
    const noDotDomainArb = fc
      .tuple(
        localPartArb,
        fc.array(domainNoDotChar, { minLength: 1, maxLength: 10 }).map((c) => c.join(''))
      )
      .map(([local, domain]) => `${local}@${domain}`)

    fc.assert(
      fc.property(noDotDomainArb, (str) => {
        expect(regexMail.test(str)).toBe(false)
      }),
      { numRuns: 100 }
    )
  })
})

// Feature: frontend-test-coverage, Property 17: Validation regex mot de passe
// **Validates: Requirements 15.2**
describe('Property 17: Validation regex mot de passe', () => {
  const lowerArb = fc.mapToConstant({ num: 26, build: (v: number) => String.fromCharCode(97 + v) })
  const upperArb = fc.mapToConstant({ num: 26, build: (v: number) => String.fromCharCode(65 + v) })
  const digitArb = fc.mapToConstant({ num: 10, build: (v: number) => String.fromCharCode(48 + v) })
  const specialArb = fc.constantFrom('-', '!', '@', '#', '^', '&', '*')

  const validPasswordArb = fc
    .tuple(
      lowerArb,
      upperArb,
      digitArb,
      specialArb,
      fc.array(fc.oneof(lowerArb, upperArb, digitArb, specialArb), { minLength: 8, maxLength: 20 })
    )
    .map(([lo, up, di, sp, rest]) => {
      const chars = [lo, up, di, sp, ...rest]
      const mid = Math.floor(chars.length / 2)
      return [...chars.slice(mid), ...chars.slice(0, mid)].join('')
    })
    .filter((s) => s.length >= 12)

  it('should match any password with 12+ chars, lowercase, uppercase, digit, special, no forbidden', () => {
    fc.assert(
      fc.property(validPasswordArb, (password) => {
        expect(regexPassword.test(password)).toBe(true)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject passwords shorter than 12 characters', () => {
    const shortPasswordArb = fc
      .tuple(
        lowerArb,
        upperArb,
        digitArb,
        specialArb,
        fc.array(fc.oneof(lowerArb, upperArb, digitArb, specialArb), { minLength: 0, maxLength: 7 })
      )
      .map(([lo, up, di, sp, rest]) => [lo, up, di, sp, ...rest].join(''))
      .filter((s) => s.length < 12)

    fc.assert(
      fc.property(shortPasswordArb, (password) => {
        expect(regexPassword.test(password)).toBe(false)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject passwords missing a required character class', () => {
    const noUpperArb = fc
      .array(fc.oneof(lowerArb, digitArb, specialArb), { minLength: 12, maxLength: 20 })
      .map((chars) => chars.join(''))
      .filter((s) => /[a-z]/.test(s) && /[0-9]/.test(s) && /[-!@#^&*]/.test(s) && !/[A-Z]/.test(s))

    fc.assert(
      fc.property(noUpperArb, (password) => {
        expect(regexPassword.test(password)).toBe(false)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject passwords containing forbidden characters', () => {
    const forbiddenCharArb = fc.constantFrom('<', '>', '"', "'")
    const withForbiddenArb = fc
      .tuple(validPasswordArb, forbiddenCharArb, fc.nat({ max: 20 }))
      .map(([pw, forbidden, pos]) => {
        const idx = pos % (pw.length + 1)
        return pw.slice(0, idx) + forbidden + pw.slice(idx)
      })

    fc.assert(
      fc.property(withForbiddenArb, (password) => {
        expect(regexPassword.test(password)).toBe(false)
      }),
      { numRuns: 100 }
    )
  })
})

// Feature: frontend-test-coverage, Property 18: Validation regex générique
// **Validates: Requirements 15.3**
describe('Property 18: Validation regex générique', () => {
  const allowedChars = fc.mapToConstant(
    { num: 26, build: (v: number) => String.fromCharCode(97 + v) },
    { num: 26, build: (v: number) => String.fromCharCode(65 + v) },
    { num: 10, build: (v: number) => String.fromCharCode(48 + v) },
    { num: 1, build: () => ' ' },
    { num: 1, build: () => ',' },
    { num: 1, build: () => '.' },
    { num: 1, build: () => "'" },
    { num: 1, build: () => '-' },
    { num: 1, build: () => '+' },
    { num: 1, build: () => 'é' },
    { num: 1, build: () => 'à' },
    { num: 1, build: () => 'è' },
    { num: 1, build: () => 'î' },
    { num: 1, build: () => 'â' },
    { num: 1, build: () => 'ô' },
    { num: 1, build: () => 'ê' },
    { num: 1, build: () => 'û' },
    { num: 1, build: () => 'ù' },
    { num: 1, build: () => '?' },
    { num: 1, build: () => '!' },
    { num: 1, build: () => '/' },
    { num: 1, build: () => '_' },
    { num: 1, build: () => '(' },
    { num: 1, build: () => ')' }
  )

  const validGenericArb = fc
    .array(allowedChars, { minLength: 1, maxLength: 50 })
    .map((chars) => chars.join(''))

  it('should match any non-empty string composed only of allowed characters', () => {
    fc.assert(
      fc.property(validGenericArb, (str) => {
        expect(regexGeneric.test(str)).toBe(true)
      }),
      { numRuns: 100 }
    )
  })

  it('should reject empty strings', () => {
    expect(regexGeneric.test('')).toBe(false)
  })

  it('should reject strings containing forbidden characters', () => {
    const forbiddenCharArb = fc.constantFrom(
      '@', '<', '>', ';', '#', '~', '`', '\\', '"', '{', '}', '|', '=', '*', '&', '%'
    )

    fc.assert(
      fc.property(
        fc.tuple(validGenericArb, forbiddenCharArb, fc.nat({ max: 50 })),
        ([validStr, forbidden, pos]) => {
          const idx = pos % (validStr.length + 1)
          const invalidStr = validStr.slice(0, idx) + forbidden + validStr.slice(idx)
          expect(regexGeneric.test(invalidStr)).toBe(false)
        }
      ),
      { numRuns: 100 }
    )
  })
})
