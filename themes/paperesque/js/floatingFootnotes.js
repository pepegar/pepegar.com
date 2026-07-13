import { docReady, onWindowResize } from "./utils.js";
import { ResizeObserver } from '@juggle/resize-observer';

const ARTICLE_CONTENT_SELECTOR = "article#main";
const FOOTNOTE_SECTION_SELECTOR = "div.footnotes[role=doc-endnotes]";
// this is a prefix-match on ID.
const INDIVIDUAL_FOOTNOTE_SELECTOR = "li[id^='fn:']";
const FLOATING_FOOTNOTE_MIN_WIDTH = 1260;
const LEFT_MARGIN_SELECTOR = ".sidepull-side";
const WIDE_CONTENT_SELECTOR = ".wide-content";
const LEFT_SIDE_CLASS = "floating-footnote-left";
const RIGHT_SIDE_CLASS = "floating-footnote-right";

// Computes an offset such that setting `top` on elemToAlign will put it
// in vertical alignment with targetAlignment.
function computeOffsetForAlignment(elemToAlign, targetAlignment) {
    const offsetParentTop = elemToAlign.offsetParent.getBoundingClientRect().top;
    // Distance between the top of the offset parent and the top of the target alignment
    return targetAlignment.getBoundingClientRect().top - offsetParentTop;
}

function computeInitialLeftLaneBottom(footnoteSection) {
    const article = document.querySelector(ARTICLE_CONTENT_SELECTOR);
    const leftMarginElement = article && article.querySelector(LEFT_MARGIN_SELECTOR);

    if (!leftMarginElement || window.getComputedStyle(leftMarginElement).display === "none") {
        return 0;
    }

    const footnoteSectionTop = footnoteSection.offsetParent.getBoundingClientRect().top;
    const leftMarginRect = leftMarginElement.getBoundingClientRect();

    return Math.max(0, leftMarginRect.bottom - footnoteSectionTop + parseInt(window.getComputedStyle(document.documentElement).fontSize));
}

function computeWideContentObstructions(footnoteSection) {
    const footnoteSectionTop = footnoteSection.offsetParent.getBoundingClientRect().top;
    const wideContentBlocks = document.querySelectorAll(WIDE_CONTENT_SELECTOR);

    return Array.prototype.map.call(wideContentBlocks, function (wideContent) {
        const wideContentRect = wideContent.getBoundingClientRect();
        const wideContentStyle = window.getComputedStyle(wideContent);
        const marginTop = parseInt(wideContentStyle.marginTop) || 0;
        const marginBottom = parseInt(wideContentStyle.marginBottom) || 0;

        return {
            top: wideContentRect.top - footnoteSectionTop - marginTop,
            bottom: wideContentRect.bottom - footnoteSectionTop + marginBottom
        };
    }).sort(function (a, b) {
        return a.top - b.top;
    });
}

function pushPastObstructions(offset, height, obstructions) {
    let adjustedOffset = offset;
    let changed = true;

    while (changed) {
        changed = false;

        Array.prototype.forEach.call(obstructions, function (obstruction) {
            const bottom = adjustedOffset + height;
            const overlaps = adjustedOffset < obstruction.bottom && bottom > obstruction.top;

            if (overlaps) {
                adjustedOffset = obstruction.bottom;
                changed = true;
            }
        });
    }

    return adjustedOffset;
}

function useLeftLane(footnote, offset, bottomOfRightLane) {
    if (offset >= bottomOfRightLane) {
        return false;
    }

    footnote.classList.add(LEFT_SIDE_CLASS);
    footnote.classList.remove(RIGHT_SIDE_CLASS);
    return true;
}

function useRightLane(footnote) {
    footnote.classList.add(RIGHT_SIDE_CLASS);
    footnote.classList.remove(LEFT_SIDE_CLASS);
}

function setFootnoteOffsets(footnotes) {
    const footnoteSection = document.querySelector(FOOTNOTE_SECTION_SELECTOR);
    const wideContentObstructions = computeWideContentObstructions(footnoteSection);
    let bottomOfRightLane = 0;
    let bottomOfLeftLane = computeInitialLeftLaneBottom(footnoteSection);

    Array.prototype.forEach.call(footnotes, function (footnote, i) {

        // In theory, don't need to escape this because IDs can't contain
        // quotes, in practice, not sure. ¯\_(ツ)_/¯

        // Get the thing that refers to the footnote
        const intextLink = document.querySelector("a.footnote-ref[href='#" + footnote.id + "']");
        // Find its "content parent"; nearest paragraph or list item or
        // whatever. We use this for alignment because it looks much cleaner.
        // If it doesn't, your paragraphs are too long :P
        // Fallback - use the same height as the link.
        const verticalAlignmentTarget = intextLink.closest('p,li') || intextLink;

        let offset = computeOffsetForAlignment(footnote, verticalAlignmentTarget);
        const footnoteStyle = window.getComputedStyle(footnote);
        const footnoteOuterHeight =
            footnote.offsetHeight +
            parseInt(footnoteStyle.marginBottom) +
            parseInt(footnoteStyle.marginTop);
        const shouldUseLeftLane = useLeftLane(footnote, offset, bottomOfRightLane);

        if (shouldUseLeftLane) {
            offset = Math.max(offset, bottomOfLeftLane);
            offset = pushPastObstructions(offset, footnoteOuterHeight, wideContentObstructions);
            bottomOfLeftLane = offset + footnoteOuterHeight;
        } else {
            useRightLane(footnote);
            offset = pushPastObstructions(offset, footnoteOuterHeight, wideContentObstructions);
            bottomOfRightLane = offset + footnoteOuterHeight;
        }

        footnote.style.top = offset + 'px';
        footnote.style.position = 'absolute';
    });
}

function clearFootnoteOffsets(footnotes) {
    // Reset all
    Array.prototype.forEach.call(footnotes, function (fn, i) {
        fn.style.top = null;
        fn.style.position = null;
        fn.classList.remove(LEFT_SIDE_CLASS);
        fn.classList.remove(RIGHT_SIDE_CLASS);
    });
}

// contract: this is idempotent; i.e. it won't wreck anything if you call it
// with the same value over and over again. Though maybe it'll wreck performance
// lol.
function updateFootnoteFloat(shouldFloat) {
    const footnoteSection = document.querySelector(FOOTNOTE_SECTION_SELECTOR);
    const footnotes = footnoteSection.querySelectorAll(INDIVIDUAL_FOOTNOTE_SELECTOR);

    if (shouldFloat) {
        // Do this first because we need styles applied before doing other
        // calculations
        footnoteSection.classList.add('floating-footnotes');
        setFootnoteOffsets(footnotes);
        subscribeToUpdates();
    } else {
        unsubscribeFromUpdates();
        clearFootnoteOffsets(footnotes);
        footnoteSection.classList.remove('floating-footnotes');
    }
}

function subscribeToUpdates() {
    const article = document.querySelector(ARTICLE_CONTENT_SELECTOR);
    // Watch for dimension changes on the thing that holds all the footnotes so
    // we can reposition as required
    resizeObserver.observe(article);
}

function unsubscribeFromUpdates() {
    resizeObserver.disconnect();
}

const notifySizeChange = function() {
    // Default state, not expanded.
    let bigEnough = false;

    return function () {
        // Pixel width at which this looks good
        let nowBigEnough = window.innerWidth >= FLOATING_FOOTNOTE_MIN_WIDTH;
        if (nowBigEnough !== bigEnough) {
            updateFootnoteFloat(nowBigEnough);
            bigEnough = nowBigEnough;
        }
    };
}();

const resizeObserver = new ResizeObserver((_entries, observer) => {
    // By virtue of the fact that we're subscribed, we know this is true.
    updateFootnoteFloat(true);
});

export default function enableFloatingFootnotes() {
    docReady(() => {
        const footnoteSection = document.querySelector(FOOTNOTE_SECTION_SELECTOR);
        const article = document.querySelector(ARTICLE_CONTENT_SELECTOR);
        const allowFloatingFootnotes = article && !article.classList.contains('no-floating-footnotes');

        // only set it all up if there's actually a footnote section and
        // we haven't explicitly disabled floating footnotes.
        if (footnoteSection && allowFloatingFootnotes) {
            onWindowResize(notifySizeChange);
        }
    });
}
